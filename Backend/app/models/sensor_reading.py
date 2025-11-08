"""
Sensor reading model for IoT sensor data.

Stores soil moisture, temperature, pH, and other sensor measurements
from IoT devices in the field.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SensorReading(BaseModel):
    """
    IoT sensor reading model.

    Represents a single reading from a sensor device in a field.
    Timestamps track when the reading was taken (may differ from created_at).
    """

    __tablename__ = "sensor_readings"

    # Foreign key to field
    field_id: Mapped[UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Sensor identification
    sensor_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Sensor measurements
    moisture_percent: Mapped[float] = mapped_column(
        Float, nullable=False, comment="Soil moisture percentage (0-100)"
    )
    temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Temperature in Celsius"
    )
    ph: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Soil pH (0-14)"
    )

    # Timestamp when reading was taken (may differ from created_at)
    reading_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="When the sensor reading was taken",
    )

    # Optional metadata
    battery_level: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Sensor battery level (0-100)"
    )
    signal_strength: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Signal strength in dBm"
    )

    # Relationship
    field: Mapped["Field"] = relationship("Field", back_populates="sensor_readings")

    def __repr__(self) -> str:
        """String representation of the sensor reading."""
        return (
            f"<SensorReading(id={self.id}, sensor={self.sensor_id}, "
            f"moisture={self.moisture_percent}%)>"
        )

