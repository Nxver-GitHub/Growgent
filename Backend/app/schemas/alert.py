"""
Pydantic schemas for Alert model.

Request and response schemas for alert API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.alert import AlertSeverity, AlertType, AgentType


class AlertBase(BaseModel):
    """Base schema for Alert with common fields."""

    alert_type: AlertType = Field(..., description="Category/type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    message: str = Field(..., min_length=1, description="Alert message")


class AlertCreate(AlertBase):
    """Schema for creating a new alert."""

    field_id: Optional[UUID] = Field(
        None, description="Field ID (optional for system-wide alerts)"
    )
    agent_type: AgentType = Field(..., description="Type of agent generating alert")


class AlertUpdate(BaseModel):
    """Schema for updating an alert (acknowledgment)."""

    acknowledged: Optional[bool] = Field(
        None, description="Whether alert has been acknowledged"
    )
    acknowledged_at: Optional[datetime] = Field(
        None, description="When alert was acknowledged"
    )


class AlertResponse(AlertBase):
    """Schema for alert response with all fields including metadata."""

    id: UUID
    field_id: Optional[UUID]
    agent_type: AgentType
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class AlertListResponse(BaseModel):
    """Schema for paginated list of alerts."""

    alerts: list[AlertResponse]
    total: int
    page: int = 1
    page_size: int = 20

