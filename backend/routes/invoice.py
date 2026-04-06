from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.connection import get_db
from schemas.invoice import (
    ErrorResponse,
    InvoiceRiskAssessment,
    InvoiceOut,
    InvoiceUploadData,
    InvoiceUploadRequest,
    InvoiceUploadResponse,
)
from services import invoice_service
from services.invoice_service import DuplicateInvoiceError

router = APIRouter(prefix="/v1", tags=["invoices"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "cipherlink-api"}


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db)):
    return invoice_service.get_all(db)


@router.post(
    "/invoices/upload",
    response_model=InvoiceUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_invoice(payload: InvoiceUploadRequest, db: Session = Depends(get_db)):
    try:
        invoice, risk_assessment = invoice_service.upload_invoice(db, payload)
        return InvoiceUploadResponse(
            data=InvoiceUploadData(
                invoice_id=invoice.invoice_id,
                hash=invoice.hash,
                risk_assessment=InvoiceRiskAssessment(**risk_assessment),
            )
        )
    except DuplicateInvoiceError as exc:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(message=str(exc)).model_dump(),
        )
