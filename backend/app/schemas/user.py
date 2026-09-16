"""Pydantic schemas for user data exchanged through the API."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Common user fields shared by create and read schemas."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class UserCreate(UserBase):
    """Payload required to create a user."""

    password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    """User representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
