# backend/app/schemas/fire_perimeter.py

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

# The geometry from the GeoJSON feature
class GeometryModel(BaseModel):
    type: str
    coordinates: list

# The properties from the GeoJSON feature
class FirePerimeterProperties(BaseModel):
    # These fields are based on the ArcGIS service schema
    poly_IncidentName: Optional[str] = Field(None, alias="poly_IncidentName")
    poly_SourceOID: Optional[int] = Field(None, alias="poly_SourceOID")
    poly_IRWINID: Optional[str] = Field(None, alias="poly_IRWINID")
    poly_CreateDate: Optional[datetime] = Field(None, alias="poly_CreateDate")
    poly_DateCurrent: Optional[datetime] = Field(None, alias="poly_DateCurrent")
    # Add other properties as needed...

# Schema for a single feature from the external API
class FirePerimeterFeature(BaseModel):
    properties: FirePerimeterProperties
    geometry: GeometryModel

# Base schema for internal use, containing the core fields
class FirePerimeterBase(BaseModel):
    id: str = Field(..., description="The unique identifier from the source.")
    agency: Optional[str] = None
    fire_name: Optional[str] = None
    properties: Dict[str, Any]

# Schema for creating a new fire perimeter in the database
class FirePerimeterCreate(FirePerimeterBase):
    geom: Dict[str, Any] # Expecting a GeoJSON geometry dictionary

# Schema for reading a fire perimeter from the database
class FirePerimeter(FirePerimeterBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True # Pydantic v2 alias for orm_mode
