from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class InvoiceItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    quantity: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)


class InvoiceUploadRequest(BaseModel):
    invoice_id: str = Field(..., min_length=1, max_length=100, examples=["INV-001"])
    supplier_id: str = Field(..., min_length=1, max_length=100, examples=["SUP-123"])
    buyer_id: str = Field(..., min_length=1, max_length=100, examples=["BUY-456"])
    amount: Decimal = Field(..., gt=0, examples=[50000])
    currency: str = Field(..., min_length=3, max_length=3, examples=["INR"])
    date: date
    items: list[InvoiceItemCreate] = Field(..., min_length=1)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper().strip()


class InvoiceRiskAssessment(BaseModel):
    score: int
    risk: str
    reasons: list[str]
    flags: dict[str, bool]


class InvoiceUploadData(BaseModel):
    invoice_id: str
    hash: str
    risk_assessment: InvoiceRiskAssessment


class InvoiceUploadResponse(BaseModel):
    status: str = "success"
    message: str = "Invoice uploaded successfully"
    data: InvoiceUploadData


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invoice_id: str
    supplier_id: str
    buyer_id: str
    amount: Decimal
    currency: str
    date: date
    hash: str
    created_at: datetime
