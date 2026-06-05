from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


ALLOWED_ORDER_STATUSES = ["pending", "paid", "cancelled", "refunded"]


class OrderItemCreate(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: list[OrderItemCreate] = Field(..., min_length=1)
    discount: float = Field(default=0, ge=0)
    created_by: str | None = Field(default=None, max_length=120)

    @field_validator("created_by")
    @classmethod
    def clean_created_by(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def validate_duplicate_items(self):
        variant_ids = [item.variant_id for item in self.items]

        if len(variant_ids) != len(set(variant_ids)):
            raise ValueError("Duplicate product variant is not allowed in same order")

        return self


class OrderStatusUpdate(BaseModel):
    status: str = Field(...)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        value = value.strip().lower()

        if value not in ALLOWED_ORDER_STATUSES:
            raise ValueError("Status must be pending, paid, cancelled or refunded")

        return value


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    variant_id: int
    quantity: int
    unit_price: float
    total_price: float

    model_config = {
        "from_attributes": True
    }


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    order_number: str
    total_amount: float
    discount: float
    final_amount: float
    status: str
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    items: list[OrderItemResponse] = []

    model_config = {
        "from_attributes": True
    }
