"""
Pydantic schemas for Field model.

Request and response schemas for field-related API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class FieldBase(BaseModel):
    """Base schema for Field with common fields."""

    farm_id: str = Field(..., description="Farm identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Field name")
    crop_type: str = Field(..., min_length=1, max_length=100, description="Crop type")
    area_hectares: float = Field(..., gt=0, description="Field area in hectares")
    location_geom: Optional[str] = Field(
        None,
        description="Field location as WKT POINT (longitude latitude) or GeoJSON",
    )
    notes: Optional[str] = Field(None, description="Optional field notes")


class FieldCreate(FieldBase):
    """Schema for creating a new field."""

    pass


class FieldUpdate(BaseModel):
    """Schema for updating a field (all fields optional)."""

    farm_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    crop_type: Optional[str] = Field(None, min_length=1, max_length=100)
    area_hectares: Optional[float] = Field(None, gt=0)
    location_geom: Optional[str] = None
    notes: Optional[str] = None


class FieldResponse(FieldBase):
    """Schema for field response with all fields including metadata."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class FieldListResponse(BaseModel):
    """Schema for paginated list of fields."""

    fields: list[FieldResponse]
    total: int
    page: int = 1
    page_size: int = 20

