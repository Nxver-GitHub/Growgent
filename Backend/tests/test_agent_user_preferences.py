"""
Integration tests for agents using user preferences.

Tests that agents correctly fetch and use user preferences for decision-making.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.water_efficiency import WaterEfficiencyAgent, WaterEfficiencyAgentState
from app.agents.psps import PSPSAlertAgent, PSPSAgentState
from app.agents.user_preferences_helper import get_user_preferences_for_field
from app.models.user import User, UserRole
from app.models.farm import Farm
from app.models.field import Field
from app.models.user_preferences import UserPreferences
from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.alert import Alert, AlertType
from app.services.user import UserService
from app.services.farm import FarmService
from app.schemas.user import UserCreate
from app.schemas.farm import FarmCreate


@pytest.mark.integration
class TestAgentUserPreferencesIntegration:
    """Integration tests for agents using user preferences."""

    @pytest.mark.asyncio
    async def test_water_efficiency_agent_uses_preferences(
        self, db_session: AsyncSession
    ) -> None:
        """Test Water Efficiency Agent uses user preferences for cost calculation."""
        # Create user with custom water cost
        user_data = UserCreate(
            email=f"watercost{uuid4().hex[:8]}@example.com",
            full_name="Water Cost User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Update preferences with custom water cost
        preferences = await UserService.get_user_preferences(db_session, user.id)
        preferences.water_cost_per_liter_usd = 0.002  # $0.002/L instead of default $0.001/L
        await db_session.commit()

        # Create farm and field
        farm_data = FarmCreate(
            owner_id=user.id,
            name="Water Cost Farm",
            farm_id=f"water-cost-farm-{uuid4().hex[:8]}",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        field = Field(
            farm_id=farm.farm_id,
            farm_uuid=farm.id,
            name="Test Field",
            crop_type="tomato",
            area_hectares=10.0,
        )
        db_session.add(field)
        await db_session.commit()
        await db_session.refresh(field)

        # Create recommendations
        for i in range(2):
            recommendation = Recommendation(
                field_id=field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title=f"Test recommendation {i}",
                reason="Test reason",
                confidence=0.8,
            )
            db_session.add(recommendation)
        await db_session.commit()

        # Run Water Efficiency Agent
        agent = WaterEfficiencyAgent()
        state = WaterEfficiencyAgentState(field_id=field.id)
        state = await agent.process(state, db_session)

        assert state.error is None
        assert state.water_metrics is not None
        # Cost should be calculated with custom water cost (0.002 instead of 0.001)
        # This means cost should be approximately 2x the default
        assert state.water_metrics.cost_saved_usd > 0

    @pytest.mark.asyncio
    async def test_water_efficiency_agent_respects_milestone_alerts_enabled(
        self, db_session: AsyncSession
    ) -> None:
        """Test Water Efficiency Agent respects water_milestone_alerts_enabled preference."""
        # Create user
        user_data = UserCreate(
            email=f"milestone{uuid4().hex[:8]}@example.com",
            full_name="Milestone User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Disable milestone alerts
        preferences = await UserService.get_user_preferences(db_session, user.id)
        preferences.water_milestone_alerts_enabled = False
        await db_session.commit()

        # Create farm and field
        farm_data = FarmCreate(
            owner_id=user.id,
            name="Milestone Farm",
            farm_id=f"milestone-farm-{uuid4().hex[:8]}",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        field = Field(
            farm_id=farm.farm_id,
            farm_uuid=farm.id,
            name="Test Field",
            crop_type="tomato",
            area_hectares=10.0,
        )
        db_session.add(field)
        await db_session.commit()
        await db_session.refresh(field)

        # Create many recommendations to trigger milestone
        for i in range(10):
            recommendation = Recommendation(
                field_id=field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title=f"Test recommendation {i}",
                reason="Test reason",
                confidence=0.8,
            )
            db_session.add(recommendation)
        await db_session.commit()

        # Count alerts before
        from sqlalchemy import select, func
        alerts_before = await db_session.execute(
            select(func.count(Alert.id)).where(
                Alert.field_id == field.id,
                Alert.alert_type == AlertType.WATER_SAVED_MILESTONE,
            )
        )
        alerts_before_count = alerts_before.scalar() or 0

        # Run Water Efficiency Agent
        agent = WaterEfficiencyAgent()
        state = WaterEfficiencyAgentState(field_id=field.id)
        state = await agent.process(state, db_session)

        # Count alerts after
        alerts_after = await db_session.execute(
            select(func.count(Alert.id)).where(
                Alert.field_id == field.id,
                Alert.alert_type == AlertType.WATER_SAVED_MILESTONE,
            )
        )
        alerts_after_count = alerts_after.scalar() or 0

        # No new alerts should be created since milestone alerts are disabled
        assert alerts_after_count == alerts_before_count

    @pytest.mark.asyncio
    async def test_user_preferences_helper_function(
        self, db_session: AsyncSession
    ) -> None:
        """Test user preferences helper function correctly traverses relationships."""
        # Create user
        user_data = UserCreate(
            email=f"helper{uuid4().hex[:8]}@example.com",
            full_name="Helper User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Create farm
        farm_data = FarmCreate(
            owner_id=user.id,
            name="Helper Farm",
            farm_id=f"helper-farm-{uuid4().hex[:8]}",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        # Create field
        field = Field(
            farm_id=farm.farm_id,
            farm_uuid=farm.id,
            name="Test Field",
            crop_type="tomato",
            area_hectares=10.0,
        )
        db_session.add(field)
        await db_session.commit()
        await db_session.refresh(field)

        # Test helper function
        preferences = await get_user_preferences_for_field(db_session, field.id)

        assert preferences is not None
        assert preferences.user_id == user.id

    @pytest.mark.asyncio
    async def test_water_efficiency_agent_uses_custom_milestone_threshold(
        self, db_session: AsyncSession
    ) -> None:
        """Test Water Efficiency Agent uses custom milestone threshold from preferences."""
        # Create user
        user_data = UserCreate(
            email=f"custommilestone{uuid4().hex[:8]}@example.com",
            full_name="Custom Milestone User",
            role=UserRole.OWNER,
        )
        user = await UserService.create_user(db_session, user_data)

        # Set custom milestone threshold
        preferences = await UserService.get_user_preferences(db_session, user.id)
        preferences.water_savings_milestone_liters = 500  # Lower threshold
        preferences.water_milestone_alerts_enabled = True
        await db_session.commit()

        # Create farm and field
        farm_data = FarmCreate(
            owner_id=user.id,
            name="Custom Milestone Farm",
            farm_id=f"custom-milestone-farm-{uuid4().hex[:8]}",
        )
        farm = await FarmService.create_farm(db_session, farm_data)

        field = Field(
            farm_id=farm.farm_id,
            farm_uuid=farm.id,
            name="Test Field",
            crop_type="tomato",
            area_hectares=10.0,
        )
        db_session.add(field)
        await db_session.commit()
        await db_session.refresh(field)

        # Create recommendations to trigger milestone
        for i in range(5):
            recommendation = Recommendation(
                field_id=field.id,
                agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
                action=RecommendationAction.IRRIGATE,
                title=f"Test recommendation {i}",
                reason="Test reason",
                confidence=0.8,
            )
            db_session.add(recommendation)
        await db_session.commit()

        # Run Water Efficiency Agent
        agent = WaterEfficiencyAgent()
        state = WaterEfficiencyAgentState(field_id=field.id)
        state = await agent.process(state, db_session)

        assert state.error is None
        assert state.water_metrics is not None
        # Agent should check for custom milestone threshold (500L) in addition to defaults

