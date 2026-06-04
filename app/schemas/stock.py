from typing import Optional

from pydantic import BaseModel, ConfigDict


class StockAdd(BaseModel):
    variant_id: int
    quantity: int
    note: Optional[str] = None
    created_by: Optional[str] = None


class StockRemove(BaseModel):
    variant_id: int
    quantity: int
    note: Optional[str] = None
    created_by: Optional[str] = None


class StockHistoryResponse(BaseModel):
    id: int
    variant_id: int
    change_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    note: Optional[str] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LowStockResponse(BaseModel):
    variant_id: int
    product_id: int
    size: str
    color: str
    sku: str
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)
