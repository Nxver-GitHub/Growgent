"""
Pydantic schemas for User model.

Defines request/response schemas for user profile management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base schema for User with common fields."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    role: UserRole = Field(UserRole.OWNER, description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    pass


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=1, max_length=255, description="User's full name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    role: Optional[UserRole] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="Whether the user account is active")
    is_verified: Optional[bool] = Field(None, description="Whether the user email is verified")
    notes: Optional[str] = Field(None, description="Additional notes")


class UserResponse(UserBase):
    """Schema for user response with all fields including metadata."""

    id: UUID
    is_active: bool
    is_verified: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class UserProfileResponse(UserResponse):
    """Extended user response including farms and preferences."""

    farms_count: int = Field(0, description="Number of farms owned by user")
    has_preferences: bool = Field(False, description="Whether user has preferences configured")

    class Config:
        """Pydantic config."""

        from_attributes = True

