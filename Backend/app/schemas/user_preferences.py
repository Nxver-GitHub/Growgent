"""
Pydantic schemas for UserPreferences model.

Defines request/response schemas for user preferences management.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserPreferencesBase(BaseModel):
    """Base schema for UserPreferences with common fields."""

    # Notification preferences
    email_notifications_enabled: bool = Field(True, description="Enable email notifications")
    sms_notifications_enabled: bool = Field(False, description="Enable SMS notifications")
    push_notifications_enabled: bool = Field(True, description="Enable push notifications")

    # Alert preferences
    alert_severity_minimum: str = Field("INFO", description="Minimum alert severity to receive")
    psps_alerts_enabled: bool = Field(True, description="Enable PSPS alerts")
    water_milestone_alerts_enabled: bool = Field(True, description="Enable water savings milestone alerts")
    fire_risk_alerts_enabled: bool = Field(True, description="Enable fire risk alerts")

    # Irrigation preferences
    water_cost_per_liter_usd: Optional[float] = Field(None, ge=0, description="Water cost per liter in USD")
    typical_irrigation_schedule: Optional[str] = Field(None, description="JSON string with typical irrigation schedule")
    irrigation_automation_enabled: bool = Field(False, description="Enable automatic irrigation recommendations")

    # Water efficiency preferences
    water_savings_milestone_liters: int = Field(1000, ge=0, description="Water savings milestone threshold in liters")
    efficiency_goal_percent: Optional[float] = Field(None, ge=0, le=100, description="Target water efficiency percentage")

    # PSPS preferences
    psps_pre_irrigation_hours: int = Field(36, ge=0, description="Hours before PSPS to recommend pre-irrigation")
    psps_auto_pre_irrigate: bool = Field(False, description="Automatically trigger pre-irrigation before PSPS")

    # Timezone and locale
    timezone: Optional[str] = Field("America/Los_Angeles", description="User timezone")
    locale: Optional[str] = Field("en-US", description="User locale")


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences."""

    user_id: UUID = Field(..., description="User ID these preferences belong to")


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences (all fields optional)."""

    email_notifications_enabled: Optional[bool] = None
    sms_notifications_enabled: Optional[bool] = None
    push_notifications_enabled: Optional[bool] = None
    alert_severity_minimum: Optional[str] = None
    psps_alerts_enabled: Optional[bool] = None
    water_milestone_alerts_enabled: Optional[bool] = None
    fire_risk_alerts_enabled: Optional[bool] = None
    water_cost_per_liter_usd: Optional[float] = Field(None, ge=0)
    typical_irrigation_schedule: Optional[str] = None
    irrigation_automation_enabled: Optional[bool] = None
    water_savings_milestone_liters: Optional[int] = Field(None, ge=0)
    efficiency_goal_percent: Optional[float] = Field(None, ge=0, le=100)
    psps_pre_irrigation_hours: Optional[int] = Field(None, ge=0)
    psps_auto_pre_irrigate: Optional[bool] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None


class UserPreferencesResponse(UserPreferencesBase):
    """Schema for user preferences response with metadata."""

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True

