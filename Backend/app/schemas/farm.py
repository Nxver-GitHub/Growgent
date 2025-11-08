"""
Pydantic schemas for Farm model.

Defines request/response schemas for farm management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FarmBase(BaseModel):
    """Base schema for Farm with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Farm name")
    farm_id: str = Field(..., min_length=1, max_length=255, description="Unique farm identifier")
    address: Optional[str] = Field(None, max_length=500, description="Farm street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State/Province")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP/Postal code")
    country: Optional[str] = Field("USA", max_length=100, description="Country")
    contact_email: Optional[str] = Field(None, description="Farm contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Farm contact phone")
    notes: Optional[str] = Field(None, description="Additional farm notes")


class FarmCreate(FarmBase):
    """Schema for creating a new farm."""

    owner_id: UUID = Field(..., description="User ID who owns this farm")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Farm latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Farm longitude")


class FarmUpdate(BaseModel):
    """Schema for updating farm information."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Farm name")
    address: Optional[str] = Field(None, max_length=500, description="Farm street address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    state: Optional[str] = Field(None, max_length=50, description="State/Province")
    zip_code: Optional[str] = Field(None, max_length=20, description="ZIP/Postal code")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    contact_email: Optional[str] = Field(None, description="Farm contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Farm contact phone")
    notes: Optional[str] = Field(None, description="Additional farm notes")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Farm latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Farm longitude")


class FarmResponse(FarmBase):
    """Schema for farm response with all fields including metadata."""

    id: UUID
    owner_id: UUID
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    fields_count: int = Field(0, description="Number of fields in this farm")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True

