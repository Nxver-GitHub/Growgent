"""
Pydantic schemas for Recommendation model.

Request and response schemas for recommendation API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.recommendation import RecommendationAction, AgentType


class RecommendationBase(BaseModel):
    """Base schema for Recommendation with common fields."""

    action: RecommendationAction = Field(..., description="Recommended action")
    title: str = Field(..., min_length=1, max_length=255, description="Recommendation title")
    reason: str = Field(..., min_length=1, description="Reason for recommendation")
    recommended_timing: Optional[datetime] = Field(
        None, description="When the action should be taken (ISO8601)"
    )
    zones_affected: Optional[str] = Field(
        None,
        max_length=500,
        description="Comma-separated list of irrigation zones affected",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0 to 1.0)"
    )
    fire_risk_reduction_percent: Optional[float] = Field(
        None, description="Estimated fire risk reduction percentage"
    )
    water_saved_liters: Optional[float] = Field(
        None, description="Estimated water saved in liters"
    )
    psps_alert: bool = Field(
        False, description="Whether this recommendation is related to PSPS"
    )


class RecommendationCreate(RecommendationBase):
    """Schema for creating a new recommendation."""

    field_id: UUID = Field(..., description="Field ID this recommendation is for")
    agent_type: AgentType = Field(..., description="Type of agent generating recommendation")


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation (limited fields)."""

    accepted: Optional[bool] = Field(None, description="Whether recommendation was accepted")
    accepted_at: Optional[datetime] = Field(None, description="When recommendation was accepted")


class RecommendationResponse(RecommendationBase):
    """Schema for recommendation response with all fields including metadata."""

    id: UUID
    field_id: UUID
    agent_type: AgentType
    accepted: bool
    accepted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for paginated list of recommendations."""

    recommendations: list[RecommendationResponse]
    total: int
    page: int = 1
    page_size: int = 20


class RecommendationRequest(BaseModel):
    """Schema for requesting a recommendation from an agent."""

    field_id: UUID = Field(..., description="Field ID to generate recommendation for")

