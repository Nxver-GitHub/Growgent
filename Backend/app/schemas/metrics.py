"""
Pydantic schemas for Water Metrics and other metrics responses.

Response schemas for metrics API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WaterMetricsResponse(BaseModel):
    """Schema for water efficiency metrics response."""

    field_id: UUID = Field(..., description="Field ID")
    water_recommended_liters: int = Field(
        ..., ge=0, description="Total water recommended by Fire-Adaptive Agent (liters)"
    )
    water_typical_liters: int = Field(
        ..., ge=0, description="Typical baseline water usage (liters)"
    )
    water_saved_liters: int = Field(
        ..., description="Water saved compared to typical (liters)"
    )
    efficiency_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Water efficiency percentage (0-100)"
    )
    cost_saved_usd: float = Field(
        ..., ge=0.0, description="Estimated cost savings in USD"
    )
    drought_stress_score: float = Field(
        ..., ge=0.0, le=100.0, description="Drought stress score (0-100, lower is better)"
    )
    last_updated: datetime = Field(..., description="When metrics were last calculated")

    class Config:
        """Pydantic config."""

        from_attributes = True


class WaterMetricsSummaryResponse(BaseModel):
    """Schema for farm-wide water metrics summary."""

    farm_id: str = Field(..., description="Farm ID")
    total_water_recommended_liters: int = Field(
        ..., ge=0, description="Total water recommended across all fields (liters)"
    )
    total_water_typical_liters: int = Field(
        ..., ge=0, description="Total typical baseline water usage (liters)"
    )
    total_water_saved_liters: int = Field(
        ..., description="Total water saved across all fields (liters)"
    )
    average_efficiency_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Average water efficiency percentage"
    )
    total_cost_saved_usd: float = Field(
        ..., ge=0.0, description="Total cost savings in USD"
    )
    field_count: int = Field(..., ge=0, description="Number of fields included")
    last_updated: datetime = Field(..., description="When summary was last calculated")

    class Config:
        """Pydantic config."""

        from_attributes = True


class FireRiskMetricsResponse(BaseModel):
    """Schema for fire risk reduction metrics response."""

    field_id: UUID = Field(..., description="Field ID")
    fire_risk_reduction_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Fire risk reduction percentage from recommendations"
    )
    current_fire_risk_level: str = Field(
        ..., description="Current fire risk level (LOW, MEDIUM, HIGH, CRITICAL)"
    )
    recommendations_applied: int = Field(
        ..., ge=0, description="Number of fire-adaptive recommendations applied"
    )
    last_updated: datetime = Field(..., description="When metrics were last calculated")

    class Config:
        """Pydantic config."""

        from_attributes = True

