"""
User preferences model for storing user-specific settings and preferences.

These preferences are used by agents to make personalized decisions.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserPreferences(BaseModel):
    """
    User preferences model.

    Stores user-specific settings that influence agent decision-making,
    including notification preferences, irrigation settings, and cost information.
    """

    __tablename__ = "user_preferences"

    # User relationship (one-to-one)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="User this preferences record belongs to",
    )

    # Notification preferences
    email_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable email notifications",
    )
    sms_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Enable SMS notifications",
    )
    push_notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable push notifications",
    )

    # Alert preferences
    alert_severity_minimum: Mapped[str] = mapped_column(
        String(20),
        default="INFO",
        nullable=False,
        comment="Minimum alert severity to receive (CRITICAL, HIGH, MEDIUM, LOW, WARNING, INFO)",
    )
    psps_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable PSPS (power shutoff) alerts",
    )
    water_milestone_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable water savings milestone alerts",
    )
    fire_risk_alerts_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Enable fire risk alerts",
    )

    # Irrigation preferences
    water_cost_per_liter_usd: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Water cost per liter in USD (for cost savings calculations)",
    )
    typical_irrigation_schedule: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON string with typical irrigation schedule by crop type",
    )
    irrigation_automation_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Enable automatic irrigation recommendations",
    )

    # Water efficiency preferences
    water_savings_milestone_liters: Mapped[int] = mapped_column(
        Integer,
        default=1000,
        nullable=False,
        comment="Water savings milestone threshold in liters (e.g., alert at 1000L saved)",
    )
    efficiency_goal_percent: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Target water efficiency percentage (0-100)",
    )

    # PSPS preferences
    psps_pre_irrigation_hours: Mapped[int] = mapped_column(
        Integer,
        default=36,
        nullable=False,
        comment="Hours before PSPS to recommend pre-irrigation",
    )
    psps_auto_pre_irrigate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Automatically trigger pre-irrigation before PSPS events",
    )

    # Timezone and locale
    timezone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="America/Los_Angeles",
        comment="User timezone (e.g., 'America/Los_Angeles')",
    )
    locale: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        default="en-US",
        comment="User locale (e.g., 'en-US')",
    )

    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="preferences",
    )

    def __repr__(self) -> str:
        """String representation of user preferences."""
        return f"<UserPreferences(user_id={self.user_id}, email_notifications={self.email_notifications_enabled})>"

