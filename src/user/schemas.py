from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.user.models import UserRoles
from utils.schemas.base import BaseSchema


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRequest(UserUpdate):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserResponse(UserUpdate):
    email_verified: Optional[bool] = False

    role: str = UserRoles.USER.value
    is_active: bool = True
    is_banned: bool = False

    # model config for orm models
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseSchema, UserResponse):
    id: Optional[str]
    updated_by: Optional[str]
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    user: UserResponse
    token: str
