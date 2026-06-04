from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvoiceItemResponse(BaseModel):
    variant_id: int
    product_name: Optional[str] = None
    size: str
    color: str
    sku: str
    quantity: int
    unit_price: float
    total_price: float


class InvoiceResponse(BaseModel):
    invoice_id: int
    invoice_number: str

    order_id: int
    order_number: str
    order_status: str

    customer_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

    items: list[InvoiceItemResponse]

    total_amount: float
    discount: float
    final_amount: float

    paid_amount: float
    due_amount: float
    payment_status: str

    created_at: datetime


class InvoiceListResponse(BaseModel):
    id: int
    invoice_number: str
    order_id: int
    created_at: datetime
