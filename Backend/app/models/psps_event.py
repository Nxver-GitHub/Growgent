"""
SQLAlchemy model for storing PSPS (Public Safety Power Shutoff) events.
"""

import enum
from typing import Optional
from uuid import UUID
from datetime import datetime # Added

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, String, Text, func, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID as SQL_UUID

from app.models.base import BaseModel


class PspsUtility(str, enum.Enum):
    """Enumeration for PSPS utilities."""
    PGE = "PGE"
    SCE = "SCE"
    SDGE = "SDGE"
    OTHER = "OTHER"


class PspsStatus(str, enum.Enum):
    """Enumeration for PSPS event status."""
    PLANNED = "planned"
    ACTIVE = "active"
    RESTORING = "restoring"
    COMPLETED = "completed"


class PspsEvent(BaseModel):
    """
    SQLAlchemy model for storing PSPS (Public Safety Power Shutoff) events.
    """

    __tablename__ = "psps_events"

    # Columns based on the data plan
    id: str = Column(String, primary_key=True, index=True)  # Unique ID from utility
    utility: PspsUtility = Column(
        SQLEnum(PspsUtility, native_enum=False),
        nullable=False,
        index=True,
        comment="Utility responsible for the PSPS event",
    )
    status: PspsStatus = Column(
        SQLEnum(PspsStatus, native_enum=False),
        nullable=False,
        index=True,
        comment="Current status of the PSPS event",
    )
    starts_at: datetime = Column(DateTime(timezone=True), nullable=False)
    ends_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)

    # GeoJSON geometry for the affected area
    geom = Column(
        Geometry(geometry_type='MULTIPOLYGON', srid=4326),
        nullable=False,
        comment="Affected area geometry as PostGIS MultiPolygon",
    )

    # Store all original properties from the FeatureServer
    properties: dict = Column(JSONB, nullable=True)

    # Internal record-keeping timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of the PSPS event."""
        return (
            f"<PspsEvent(id='{self.id}', utility='{self.utility.value}', "
            f"status='{self.status.value}', starts_at='{self.starts_at}')>"
        )
