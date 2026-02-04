import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.schemas.account import AccountRead


class UserBase(BaseModel):
    """Base schema for user data with shared attributes."""

    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)


# Schemas for basic users:
class UserCreate(UserBase):
    """Schema for user registration (public endpoint)."""

    password: str = Field(min_length=8, max_length=32)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(UserBase):
    """Schema for reading user data in API responses."""

    id: int
    created_at: datetime
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Schema for partial user profile updates by the user themselves."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=32)


# Schemas for admin users:
class UserAdminReadWithAccounts(UserRead):
    """Detailed user schema for admin including user's accounts."""

    accounts: list[AccountRead] = []
    deleted_at: datetime | None = None
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)


class UserAdminCreate(UserCreate):
    """Schema for admin-level user creation with privilege management."""

    is_admin: bool = False


class UserAdminUpdate(UserUpdate):
    """Schema for admin-level user modification."""

    is_admin: bool | None = None
