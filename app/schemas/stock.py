from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class StockBase(BaseModel):
    variant_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    note: str | None = Field(default=None, max_length=255)
    created_by: str | None = Field(default=None, max_length=120)

    @field_validator("note", "created_by")
    @classmethod
    def clean_optional_text(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None


class StockAdd(StockBase):
    pass


class StockRemove(StockBase):
    pass


class StockChangeCreate(StockBase):
    pass


class StockHistoryResponse(BaseModel):
    id: int
    variant_id: int
    change_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    note: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class LowStockResponse(BaseModel):
    id: int
    product_id: int
    size: str
    color: str
    sku: str
    stock_quantity: int
    sell_price: float
    is_active: bool

    model_config = {
        "from_attributes": True
    }


# Compatibility aliases for old imports
StockCreate = StockAdd
StockUpdate = StockAdd
StockAdjustment = StockAdd
