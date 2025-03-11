from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from src.user.models import UserRoles
from utils.schemas.base import BaseSchema


class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRequest(UserUpdate):
    firstname: str
    lastname: str
    email: EmailStr | None
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


class ForgotRequest(BaseModel):
    email: EmailStr


class ResetRequest(BaseModel):
    token: str
    new_password: str


class UserStatsResponse(BaseModel):
    total_session: int
    avg_score: float
    high_score: float
