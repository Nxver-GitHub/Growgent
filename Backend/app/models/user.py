"""
User model for user accounts and authentication.

Stores user account information, authentication details, and links to farms.
"""

import enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.farm import Farm
    from app.models.user_preferences import UserPreferences


class UserRole(str, enum.Enum):
    """User role enumeration."""
    OWNER = "owner"
    MANAGER = "manager"
    WORKER = "worker"
    ADMIN = "admin"


class User(BaseModel):
    """
    User account model.

    Represents a user account with authentication and profile information.
    Users can own or manage multiple farms.
    """

    __tablename__ = "users"

    # Authentication & identification
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="User email address (used for login)",
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="User's full name",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="User's phone number",
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, native_enum=False),
        nullable=False,
        default=UserRole.OWNER,
        index=True,
        comment="User role: owner, manager, worker, admin",
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether the user account is active",
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the user email is verified",
    )

    # Optional metadata
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes about the user",
    )

    # Relationships
    farms: Mapped[list["Farm"]] = relationship(
        "Farm",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    preferences: Mapped[Optional["UserPreferences"]] = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email={self.email}, name={self.full_name})>"

