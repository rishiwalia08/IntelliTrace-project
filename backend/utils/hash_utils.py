import hashlib
from datetime import date
from decimal import Decimal


def generate_invoice_hash(
    *,
    invoice_id: str,
    supplier_id: str,
    buyer_id: str,
    amount: Decimal,
    invoice_date: date,
) -> str:
    """Generate a deterministic SHA256 fingerprint for deduplication."""
    normalized_amount = f"{Decimal(amount):.2f}"
    payload = "|".join(
        [
            invoice_id.strip(),
            supplier_id.strip(),
            buyer_id.strip(),
            normalized_amount,
            invoice_date.isoformat(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
