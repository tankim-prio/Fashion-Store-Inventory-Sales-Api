from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Category name cannot be empty")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
