from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.invoice import Invoice
from models.invoice_item import InvoiceItem
from schemas.invoice import InvoiceUploadRequest
from services import graph_service
from services.risk_engine import build_risk_assessment
from utils.hash_utils import generate_invoice_hash
from utils.logger import get_logger

logger = get_logger(__name__)


class DuplicateInvoiceError(Exception):
    """Raised when the invoice business identifier or deterministic hash already exists."""

    def __init__(self, message: str = "Duplicate invoice detected") -> None:
        super().__init__(message)


def get_all(db: Session) -> list[Invoice]:
    """Fetch all invoices sorted by latest creation time."""
    stmt = select(Invoice).order_by(Invoice.created_at.desc())
    return list(db.scalars(stmt).all())


def _safe_ratio(numerator: Decimal, denominator: Decimal) -> float:
    if denominator <= 0:
        return 0.0
    return float(max(Decimal("0"), min(Decimal("1"), numerator / denominator)))


def _invoice_similarity_score(
    payload: InvoiceUploadRequest,
    candidate: Invoice,
) -> float:
    amount_similarity = _safe_ratio(
        min(payload.amount, candidate.amount), max(payload.amount, candidate.amount)
    )

    day_diff = abs((payload.date - candidate.date).days)
    date_similarity = max(0.0, 1.0 - (day_diff / 30.0))

    invoice_id_similarity = 1.0 if payload.invoice_id == candidate.invoice_id else 0.0

    score = 0.0
    if payload.supplier_id == candidate.supplier_id:
        score += 0.25
    if payload.buyer_id == candidate.buyer_id:
        score += 0.25
    score += amount_similarity * 0.30
    score += date_similarity * 0.15
    score += invoice_id_similarity * 0.05

    return round(min(score, 1.0), 4)


def _compute_duplicate_signals(db: Session, payload: InvoiceUploadRequest) -> dict[str, float | bool]:
    candidate_stmt = (
        select(Invoice)
        .where(or_(Invoice.supplier_id == payload.supplier_id, Invoice.buyer_id == payload.buyer_id))
        .order_by(Invoice.created_at.desc())
        .limit(200)
    )
    candidates = list(db.scalars(candidate_stmt).all())

    if not candidates:
        return {"duplicate": False, "similarity_score": 0.0}

    best_similarity = max(_invoice_similarity_score(payload, candidate) for candidate in candidates)
    return {
        "duplicate": best_similarity > 0.9,
        "similarity_score": best_similarity,
    }


def _supplier_historical_average(db: Session, supplier_id: str) -> float | None:
    avg_stmt = select(func.avg(Invoice.amount)).where(Invoice.supplier_id == supplier_id)
    avg_amount = db.scalar(avg_stmt)
    if avg_amount is None:
        return None
    return float(avg_amount)


def upload_invoice(db: Session, payload: InvoiceUploadRequest) -> tuple[Invoice, dict[str, object]]:
    """Persist invoice and line items after deterministic duplicate validation."""
    invoice_hash = generate_invoice_hash(
        invoice_id=payload.invoice_id,
        supplier_id=payload.supplier_id,
        buyer_id=payload.buyer_id,
        amount=payload.amount,
        invoice_date=payload.date,
    )

    duplicate_stmt = select(Invoice).where(
        or_(Invoice.invoice_id == payload.invoice_id, Invoice.hash == invoice_hash)
    )
    duplicate = db.scalar(duplicate_stmt)

    if duplicate:
        logger.warning(
            "duplicate_invoice_upload_attempt",
            extra={
                "invoice_id": payload.invoice_id,
                "supplier_id": payload.supplier_id,
                "buyer_id": payload.buyer_id,
                "hash": invoice_hash,
            },
        )
        raise DuplicateInvoiceError()

    duplicate_signals = _compute_duplicate_signals(db, payload)
    historical_average = _supplier_historical_average(db, payload.supplier_id)

    invoice = Invoice(
        invoice_id=payload.invoice_id,
        supplier_id=payload.supplier_id,
        buyer_id=payload.buyer_id,
        amount=payload.amount,
        currency=payload.currency,
        date=payload.date,
        hash=invoice_hash,
    )

    invoice.items = [
        InvoiceItem(name=item.name, quantity=item.quantity, price=item.price) for item in payload.items
    ]

    db.add(invoice)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning(
            "duplicate_invoice_upload_race_condition",
            extra={"invoice_id": payload.invoice_id, "hash": invoice_hash},
        )
        raise DuplicateInvoiceError() from exc
    db.refresh(invoice)

    logger.info(
        "invoice_uploaded",
        extra={
            "invoice_id": invoice.invoice_id,
            "supplier_id": invoice.supplier_id,
            "buyer_id": invoice.buyer_id,
            "hash": invoice.hash,
        },
    )

    fraud_signals = graph_service.register_transaction_and_detect(invoice)

    if fraud_signals.get("cycle_detected"):
        logger.warning(
            "cycle_detection_event",
            extra={"invoice_id": invoice.invoice_id, "cycles": fraud_signals.get("cycles", [])},
        )

    if fraud_signals.get("suspicious_nodes"):
        logger.warning(
            "suspicious_hub_nodes_detected",
            extra={
                "invoice_id": invoice.invoice_id,
                "suspicious_nodes": fraud_signals.get("suspicious_nodes", []),
            },
        )

    risk_assessment = build_risk_assessment(
        graph_signals=fraud_signals,
        duplicate_signals=duplicate_signals,
        invoice_data={
            "amount": float(payload.amount),
            "supplier_id": payload.supplier_id,
            "historical_average": historical_average,
            "invoice_date": payload.date.isoformat() if isinstance(payload.date, date) else str(payload.date),
        },
    )

    logger.info(
        "invoice_risk_scored",
        extra={
            "invoice_id": invoice.invoice_id,
            "score": risk_assessment["score"],
            "risk": risk_assessment["risk"],
        },
    )

    if risk_assessment["risk"] == "HIGH":
        logger.warning(
            "high_risk_invoice_alert",
            extra={
                "invoice_id": invoice.invoice_id,
                "score": risk_assessment["score"],
                "reasons": risk_assessment["reasons"],
            },
        )

    return invoice, risk_assessment
