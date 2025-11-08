"""
Recommendation model for agent-generated irrigation recommendations.

Stores recommendations from the Fire-Adaptive Irrigation Agent and other
agents, including action type, timing, confidence, and impact metrics.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import BaseModel


class RecommendationAction(str, enum.Enum):
    """Enumeration of recommendation action types."""

    IRRIGATE = "IRRIGATE"
    DELAY = "DELAY"
    MONITOR = "MONITOR"
    PRE_IRRIGATE = "PRE_IRRIGATE"  # Pre-PSPS irrigation


class AgentType(str, enum.Enum):
    """Enumeration of agent types that generate recommendations."""

    FIRE_ADAPTIVE_IRRIGATION = "FIRE_ADAPTIVE_IRRIGATION"
    WATER_EFFICIENCY = "WATER_EFFICIENCY"
    PSPS_ANTICIPATION = "PSPS_ANTICIPATION"


class Recommendation(BaseModel):
    """
    Agent recommendation model.

    Represents a recommendation from an agent (e.g., Fire-Adaptive Irrigation)
    with action, timing, confidence, and impact metrics.
    """

    __tablename__ = "recommendations"

    # Foreign key to field
    field_id: Mapped[UUID] = mapped_column(
        ForeignKey("fields.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Agent information
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType),
        nullable=False,
        index=True,
        comment="Type of agent that generated this recommendation",
    )

    # Recommendation details
    action: Mapped[RecommendationAction] = mapped_column(
        SQLEnum(RecommendationAction),
        nullable=False,
        index=True,
        comment="Recommended action (IRRIGATE, DELAY, MONITOR, PRE_IRRIGATE)",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)

    # Timing
    recommended_timing: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="When the action should be taken (ISO8601)",
    )

    # Zones affected (comma-separated or JSON array)
    zones_affected: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Comma-separated list of irrigation zones affected",
    )

    # Confidence and metrics
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Confidence score (0.0 to 1.0)",
    )
    fire_risk_reduction_percent: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated fire risk reduction percentage",
    )
    water_saved_liters: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Estimated water saved in liters",
    )

    # PSPS-related
    psps_alert: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether this recommendation is related to PSPS",
    )

    # Status
    accepted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether the recommendation was accepted by the user",
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the recommendation was accepted",
    )

    # Relationship
    field: Mapped["Field"] = relationship("Field", back_populates="recommendations")

    def __repr__(self) -> str:
        """String representation of the recommendation."""
        return (
            f"<Recommendation(id={self.id}, action={self.action.value}, "
            f"agent={self.agent_type.value}, confidence={self.confidence})>"
        )

