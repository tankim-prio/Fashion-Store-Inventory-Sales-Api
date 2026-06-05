from datetime import datetime
from pydantic import BaseModel, Field, field_validator


ALLOWED_PAYMENT_METHODS = ["cash", "bkash", "nagad", "card"]
ALLOWED_PAYMENT_STATUSES = ["pending", "paid", "failed", "refunded"]


class PaymentCreate(BaseModel):
    order_id: int = Field(..., gt=0)
    payment_method: str = Field(...)
    amount: float = Field(..., gt=0)
    status: str = Field(default="paid")
    transaction_id: str | None = Field(default=None, max_length=120)

    @field_validator("payment_method")
    @classmethod
    def validate_method(cls, value: str):
        value = value.strip().lower()

        if value not in ALLOWED_PAYMENT_METHODS:
            raise ValueError("Payment method must be cash, bkash, nagad or card")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()

        if value not in ALLOWED_PAYMENT_STATUSES:
            raise ValueError("Payment status must be pending, paid, failed or refunded")

        return value

    @field_validator("transaction_id")
    @classmethod
    def clean_transaction_id(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None


class PaymentStatusUpdate(BaseModel):
    status: str = Field(...)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()

        if value not in ALLOWED_PAYMENT_STATUSES:
            raise ValueError("Payment status must be pending, paid, failed or refunded")

        return value


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: str | None = None
    paid_at: datetime | None = None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


# Compatibility name if old router imports this
PaymentUpdate = PaymentStatusUpdate
