from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    phone: str = Field(..., min_length=5, max_length=20, pattern=r"^\+?[0-9]{5,20}$")
    email: EmailStr | None = None
    address: str | None = Field(default=None, max_length=300)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Customer name cannot be empty")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        value = value.strip()

        if not value:
            raise ValueError("Phone number cannot be empty")

        return value

    @field_validator("address")
    @classmethod
    def clean_address(cls, value: str | None):
        if value is None:
            return value

        value = value.strip()
        return value or None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }
