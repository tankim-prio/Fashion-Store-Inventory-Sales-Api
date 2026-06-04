from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    category_id: int
    brand: Optional[str] = None
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category_id: int
    brand: Optional[str] = None
    description: Optional[str] = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
