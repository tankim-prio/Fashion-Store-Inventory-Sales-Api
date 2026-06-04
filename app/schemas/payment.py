from typing import Optional

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    amount: float
    status: str = "paid"
    transaction_id: Optional[str] = None


class PaymentUpdate(BaseModel):
    status: str
    transaction_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
