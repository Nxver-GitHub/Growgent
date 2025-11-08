"""
Pydantic schemas for SensorReading model.

Request and response schemas for sensor reading API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class SensorReadingBase(BaseModel):
    """Base schema for SensorReading with common fields."""

    sensor_id: str = Field(..., min_length=1, max_length=255, description="Sensor ID")
    moisture_percent: float = Field(
        ..., ge=0, le=100, description="Soil moisture percentage (0-100)"
    )
    temperature: Optional[float] = Field(
        None, description="Temperature in Celsius"
    )
    ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH (0-14)")
    reading_timestamp: datetime = Field(
        ..., description="When the sensor reading was taken"
    )
    battery_level: Optional[float] = Field(
        None, ge=0, le=100, description="Sensor battery level (0-100)"
    )
    signal_strength: Optional[float] = Field(
        None, description="Signal strength in dBm"
    )


class SensorReadingCreate(SensorReadingBase):
    """Schema for creating a new sensor reading."""

    field_id: UUID = Field(..., description="Field ID this reading belongs to")


class SensorReadingResponse(SensorReadingBase):
    """Schema for sensor reading response with all fields including metadata."""

    id: UUID
    field_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class SensorReadingListResponse(BaseModel):
    """Schema for paginated list of sensor readings."""

    readings: list[SensorReadingResponse]
    total: int
    page: int = 1
    page_size: int = 20

