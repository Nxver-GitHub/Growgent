"""
Pydantic schemas for Zone model.

Request and response schemas for zone-related API endpoints.
Supports GeoJSON geometry input/output.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.zone import ZoneType, RiskLevel


class ZoneBase(BaseModel):
    """Base schema for Zone with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Zone name")
    description: Optional[str] = Field(None, description="Zone description")
    zone_type: ZoneType = Field(..., description="Zone type: fire_risk, psps, irrigation, or custom")
    risk_level: RiskLevel = Field(..., description="Risk level: critical, high, moderate, low, or info")
    geometry: Optional[Dict[str, Any]] = Field(
        None,
        description="Zone geometry as GeoJSON (Polygon, MultiPolygon, etc.)",
    )
    field_id: Optional[str] = Field(None, description="Optional field ID link")
    farm_id: Optional[str] = Field(None, description="Optional farm ID for farm-level zones")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional JSON metadata")

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate GeoJSON geometry structure.

        Args:
            v: GeoJSON geometry dict

        Returns:
            Validated geometry dict

        Raises:
            ValueError: If geometry is invalid
        """
        if v is None:
            return v

        # Basic GeoJSON validation
        if not isinstance(v, dict):
            raise ValueError("Geometry must be a GeoJSON object")
        if "type" not in v:
            raise ValueError("Geometry must have a 'type' field")
        if v["type"] not in ["Polygon", "MultiPolygon", "Point", "LineString", "MultiLineString"]:
            raise ValueError(
                f"Unsupported geometry type: {v['type']}. "
                "Supported types: Polygon, MultiPolygon, Point, LineString, MultiLineString"
            )
        if "coordinates" not in v:
            raise ValueError("Geometry must have a 'coordinates' field")

        return v


class ZoneCreate(ZoneBase):
    """Schema for creating a new zone."""

    pass


class ZoneUpdate(BaseModel):
    """Schema for updating a zone (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    zone_type: Optional[ZoneType] = None
    risk_level: Optional[RiskLevel] = None
    geometry: Optional[Dict[str, Any]] = None
    field_id: Optional[str] = None
    farm_id: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None

    @field_validator("geometry")
    @classmethod
    def validate_geometry(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate GeoJSON geometry structure."""
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError("Geometry must be a GeoJSON object")
        if "type" not in v:
            raise ValueError("Geometry must have a 'type' field")
        if v["type"] not in ["Polygon", "MultiPolygon", "Point", "LineString", "MultiLineString"]:
            raise ValueError(
                f"Unsupported geometry type: {v['type']}. "
                "Supported types: Polygon, MultiPolygon, Point, LineString, MultiLineString"
            )
        if "coordinates" not in v:
            raise ValueError("Geometry must have a 'coordinates' field")

        return v


class ZoneResponse(ZoneBase):
    """Schema for zone response with all fields including metadata."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class ZoneListResponse(BaseModel):
    """Schema for paginated list of zones."""

    zones: list[ZoneResponse]
    total: int
    page: int = 1
    page_size: int = 20

