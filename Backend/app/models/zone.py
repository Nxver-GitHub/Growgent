"""
Zone model for representing risk zones with spatial geometry.

Zones support GeoJSON geometry storage using PostGIS, link to farms/fields,
and include zone types (fire_risk, psps, irrigation, custom) and risk levels
(critical, high, moderate, low, info).
"""

import enum
from typing import Optional, TYPE_CHECKING

from geoalchemy2 import Geometry
from sqlalchemy import String, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.field import Field


class ZoneType(str, enum.Enum):
    """Zone type enumeration."""

    FIRE_RISK = "fire_risk"
    PSPS = "psps"
    IRRIGATION = "irrigation"
    CUSTOM = "custom"


class RiskLevel(str, enum.Enum):
    """Risk level enumeration."""

    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    INFO = "info"


class Zone(BaseModel):
    """
    Risk zone model with spatial geometry.

    Represents a geographic zone with PostGIS geometry (Polygon, MultiPolygon, etc.)
    that can be linked to fields and categorized by type and risk level.
    """

    __tablename__ = "zones"

    # Zone identification
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Zone classification
    zone_type: Mapped[ZoneType] = mapped_column(
        SQLEnum(ZoneType, native_enum=False),
        nullable=False,
        index=True,
        comment="Zone type: fire_risk, psps, irrigation, or custom",
    )
    risk_level: Mapped[RiskLevel] = mapped_column(
        SQLEnum(RiskLevel, native_enum=False),
        nullable=False,
        index=True,
        comment="Risk level: critical, high, moderate, low, or info",
    )

    # Spatial geometry (PostGIS - supports Polygon, MultiPolygon, etc.)
    # Format: GeoJSON geometry in WGS84 (EPSG:4326)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326),
        nullable=True,
        comment="Zone geometry as PostGIS geometry (Polygon, MultiPolygon, etc.)",
    )

    # Optional link to field (zones can be farm-level or field-specific)
    field_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, comment="Optional field ID link"
    )

    # Farm identifier (for farm-level zones)
    farm_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, index=True, comment="Optional farm ID for farm-level zones"
    )

    # Optional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved name)
    extra_metadata: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional JSON metadata"
    )

    # Relationships
    # Note: Using string reference to avoid circular imports
    # field: Mapped[Optional["Field"]] = relationship("Field", back_populates="zones")

    def __repr__(self) -> str:
        """String representation of the zone."""
        return (
            f"<Zone(id={self.id}, name={self.name}, "
            f"type={self.zone_type.value}, risk={self.risk_level.value})>"
        )

