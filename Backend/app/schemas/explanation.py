"""
Pydantic schemas for agent explanations and transparency.

Provides detailed breakdowns of agent decision-making processes.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.recommendation import RecommendationAction, AgentType


class DecisionFactor(BaseModel):
    """A single factor that influenced the agent's decision."""

    name: str = Field(..., description="Name of the factor")
    value: float = Field(..., description="Numeric value of the factor")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    weight: float = Field(..., ge=0.0, le=1.0, description="Weight/importance of this factor")
    impact: str = Field(..., description="How this factor influenced the decision")
    threshold_met: Optional[bool] = Field(
        None, description="Whether this factor met a decision threshold"
    )


class DataSource(BaseModel):
    """Information about a data source used by the agent."""

    name: str = Field(..., description="Name of the data source")
    type: str = Field(..., description="Type of data source (sensor, API, etc.)")
    available: bool = Field(..., description="Whether data was available")
    quality_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Data quality score (0.0 to 1.0)"
    )
    last_updated: Optional[datetime] = Field(None, description="When data was last updated")
    notes: Optional[str] = Field(None, description="Additional notes about the data")


class AlternativeScenario(BaseModel):
    """An alternative decision scenario that was considered."""

    action: RecommendationAction = Field(..., description="Alternative action considered")
    reason: str = Field(..., description="Why this alternative was considered")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence if this action was taken")
    why_not_chosen: str = Field(..., description="Why this alternative was not selected")


class ConfidenceBreakdown(BaseModel):
    """Breakdown of confidence score components."""

    data_quality: float = Field(..., ge=0.0, le=1.0, description="Data quality component")
    decision_certainty: float = Field(
        ..., ge=0.0, le=1.0, description="Decision certainty component"
    )
    model_confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Model confidence component"
    )
    overall: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")


class AgentExplanation(BaseModel):
    """Comprehensive explanation of an agent's decision."""

    recommendation_id: UUID = Field(..., description="ID of the recommendation being explained")
    agent_type: AgentType = Field(..., description="Type of agent that made the decision")
    action: RecommendationAction = Field(..., description="Recommended action")

    # Summary
    summary: str = Field(..., description="High-level summary of the decision")
    reasoning: str = Field(..., description="Detailed reasoning for the decision")

    # Decision factors
    decision_factors: List[DecisionFactor] = Field(
        default_factory=list, description="Factors that influenced the decision"
    )

    # Data sources
    data_sources: List[DataSource] = Field(
        default_factory=list, description="Data sources used in the decision"
    )

    # Confidence breakdown
    confidence_breakdown: ConfidenceBreakdown = Field(
        ..., description="Breakdown of confidence score"
    )

    # Alternatives considered
    alternatives_considered: List[AlternativeScenario] = Field(
        default_factory=list, description="Alternative scenarios that were considered"
    )

    # Impact metrics
    fire_risk_reduction_percent: Optional[float] = Field(
        None, description="Estimated fire risk reduction percentage"
    )
    water_saved_liters: Optional[float] = Field(
        None, description="Estimated water saved in liters"
    )

    # Timing
    recommended_timing: Optional[datetime] = Field(
        None, description="When the action should be taken"
    )
    urgency: str = Field(
        ..., description="Urgency level (low, medium, high, critical)"
    )

    # Metadata
    decision_timestamp: datetime = Field(..., description="When the decision was made")
    data_quality_score: float = Field(
        ..., ge=0.0, le=1.0, description="Overall data quality score"
    )


class ExplanationRequest(BaseModel):
    """Request schema for getting an explanation."""

    recommendation_id: UUID = Field(..., description="ID of the recommendation to explain")
    include_alternatives: bool = Field(
        True, description="Whether to include alternative scenarios"
    )
    include_data_sources: bool = Field(
        True, description="Whether to include detailed data source information"
    )

