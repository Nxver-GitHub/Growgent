"""
Field model for representing agricultural fields.

Fields contain spatial geometry (PostGIS), crop information, and
are linked to sensor readings and recommendations.
"""

from typing import Optional, TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.sensor_reading import SensorReading
    from app.models.recommendation import Recommendation
    from app.models.alert import Alert


class Field(BaseModel):
    """
    Agricultural field model.

    Represents a physical field on a farm with location, crop type,
    and area information. Uses PostGIS for spatial queries.
    """

    __tablename__ = "fields"

    # Farm identifier (string for now; could be FK to Farm model later)
    farm_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Field identification
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    crop_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    area_hectares: Mapped[float] = mapped_column(Float, nullable=False)

    # Spatial location (PostGIS Point geometry)
    # Format: POINT(longitude latitude) in WGS84 (EPSG:4326)
    location_geom: Mapped[Optional[str]] = mapped_column(
        Geometry("POINT", srid=4326),
        nullable=True,
        comment="Field location as PostGIS Point (longitude, latitude)",
    )

    # Optional metadata
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    sensor_readings: Mapped[list["SensorReading"]] = relationship(
        "SensorReading",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    alerts: Mapped[list["Alert"]] = relationship(
        "Alert",
        back_populates="field",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of the field."""
        return f"<Field(id={self.id}, name={self.name}, crop={self.crop_type})>"

