from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class ProductVariantBase(BaseModel):
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1, max_length=30)
    color: str = Field(..., min_length=2, max_length=50)
    buy_price: float = Field(..., ge=0)
    sell_price: float = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    sku: str = Field(..., min_length=3, max_length=100)

    @field_validator("size", "color", "sku")
    @classmethod
    def clean_text(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value

    @model_validator(mode="after")
    def validate_prices(self):
        if self.sell_price < self.buy_price:
            raise ValueError("Sell price cannot be lower than buy price")

        return self


class ProductVariantCreate(ProductVariantBase):
    pass


class ProductVariantUpdate(ProductVariantBase):
    pass


class ProductVariantResponse(ProductVariantBase):
    id: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
