from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str


class UserCreateByAdmin(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "staff"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
