from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    category_id: int = Field(..., gt=0)
    brand: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Product name cannot be empty")

        return value

    @field_validator("brand", "description")
    @classmethod
    def clean_optional_text(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
