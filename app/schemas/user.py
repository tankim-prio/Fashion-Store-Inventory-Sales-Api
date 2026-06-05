from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    is_active: bool


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
