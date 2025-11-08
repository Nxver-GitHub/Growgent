"""
Farm model for representing farms owned or managed by users.

Farms contain multiple fields and have location, contact, and operational information.
"""

from typing import Optional, TYPE_CHECKING
from uuid import UUID

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.field import Field


class Farm(BaseModel):
    """
    Farm model.

    Represents a farm owned or managed by a user. Contains location,
    contact information, and links to fields.
    """

    __tablename__ = "farms"

    # Owner relationship
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this farm",
    )

    # Farm identification
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Farm name",
    )
    farm_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique farm identifier (legacy/compatibility field)",
    )

    # Location
    # Format: POINT(longitude latitude) in WGS84 (EPSG:4326)
    location_geom: Mapped[Optional[str]] = mapped_column(
        Geometry("POINT", srid=4326),
        nullable=True,
        comment="Farm location as PostGIS Point (longitude, latitude)",
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Farm street address",
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="City",
    )
    state: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="State/Province",
    )
    zip_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="ZIP/Postal code",
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="USA",
        comment="Country",
    )

    # Contact information
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Farm contact email (may differ from owner email)",
    )
    contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Farm contact phone",
    )

    # Optional metadata
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional farm notes",
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="farms",
    )
    fields: Mapped[list["Field"]] = relationship(
        "Field",
        back_populates="farm",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of the farm."""
        return f"<Farm(id={self.id}, name={self.name}, farm_id={self.farm_id})>"

