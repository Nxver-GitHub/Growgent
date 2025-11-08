"""
Pydantic schemas for PspsEvent model.

Defines request/response schemas for PSPS event management.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.psps_event import PspsUtility, PspsStatus


# The geometry from the GeoJSON feature
class GeometryModel(BaseModel):
    """GeoJSON Geometry model."""
    type: str
    coordinates: List[Any]


# The properties from the GeoJSON feature (example, adjust based on actual utility data)
class PspsEventProperties(BaseModel):
    """Properties from a PSPS GeoJSON feature."""
    # Example fields, these will vary significantly by utility (PG&E, SCE, SDG&E)
    # We'll use generic names and rely on 'extra_metadata' for specifics
    utility_id: Optional[str] = Field(None, alias="id", description="Utility's internal ID for the event")
    utility_name: Optional[str] = Field(None, alias="utility", description="Name of the utility")
    event_status: Optional[str] = Field(None, alias="status", description="Status of the event (e.g., 'active', 'planned')")
    start_time: Optional[datetime] = Field(None, alias="start_time", description="Event start time")
    end_time: Optional[datetime] = Field(None, alias="end_time", description="Event end time")
    affected_customers: Optional[int] = Field(None, alias="customers", description="Number of affected customers")
    reason: Optional[str] = Field(None, description="Reason for the PSPS event")
    # Add other common properties as needed, or rely on extra_metadata

    class Config:
        """Pydantic config."""
        extra = "allow" # Allow extra fields not explicitly defined


# Schema for a single feature from the external API
class PspsEventFeature(BaseModel):
    """Schema for a single PSPS event GeoJSON feature from external API."""
    type: str = "Feature"
    properties: PspsEventProperties
    geometry: GeometryModel


# Base schema for internal use, containing the core fields
class PspsEventBase(BaseModel):
    """Base schema for PspsEvent model."""
    id: str = Field(..., description="The unique identifier from the source utility.")
    utility: PspsUtility = Field(..., description="Utility responsible for the PSPS event.")
    status: PspsStatus = Field(..., description="Current status of the PSPS event.")
    starts_at: datetime = Field(..., description="Event start time.")
    ends_at: Optional[datetime] = Field(None, description="Event end time.")
    properties: Dict[str, Any] = Field(..., description="All original properties from the source.")


# Schema for creating a new PSPS event in the database
class PspsEventCreate(PspsEventBase):
    """Schema for creating a new PSPS event."""
    geom: Dict[str, Any] = Field(..., description="GeoJSON geometry dictionary for the affected area.")


# Schema for reading a PSPS event from the database
class PspsEventResponse(PspsEventBase):
    """Schema for PSPS event response with all fields including metadata."""
    geom: Dict[str, Any] = Field(..., description="GeoJSON geometry dictionary for the affected area.")
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True # Pydantic v2 alias for orm_mode


class PspsEventListResponse(BaseModel):
    """Schema for paginated list of PSPS events."""
    psps_events: List[PspsEventResponse]
    total: int
    page: int = 1
    page_size: int = 20
