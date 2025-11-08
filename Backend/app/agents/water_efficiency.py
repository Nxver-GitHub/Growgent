"""
Water Efficiency Agent.

This agent analyzes irrigation recommendations and actual water usage
to calculate water savings and identify inefficiencies.
"""

import logging
import random
from typing import Any, Dict, Optional, TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentState, BaseAgent
from app.services.recommendation import RecommendationService
from app.models.recommendation import RecommendationAction
from app.agents.user_preferences_helper import get_user_preferences_for_field

if TYPE_CHECKING:
    from app.models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


class WaterEfficiencyAgentState(AgentState):
    """
    State for the Water Efficiency Agent.
    """
    # Input
    field_id: UUID
    time_period: str = "last_30_days"  # e.g., "last_7_days", "last_30_days", "season"

    # Fetched data
    recommendations: list[Dict[str, Any]] = []
    actual_irrigation_data: list[Dict[str, Any]] = []

    # Calculated values
    water_metrics: Optional[Dict[str, Any]] = None
    total_water_recommended: float = 0.0  # in liters
    total_water_used: float = 0.0  # in liters
    water_saved: float = 0.0  # in liters
    efficiency_score: float = 0.0  # 0.0 to 1.0
    inefficiencies: list[str] = []


class WaterEfficiencyAgent(BaseAgent):
    """
    Water Efficiency Agent.

    Analyzes water usage vs. recommendations to provide efficiency metrics.
    Uses user preferences for milestone thresholds and alert settings.
    """

    def __init__(self) -> None:
        """Initialize Water Efficiency Agent."""
        super().__init__("WaterEfficiencyAgent")

    async def process(
        self, state: WaterEfficiencyAgentState, db: AsyncSession
    ) -> WaterEfficiencyAgentState:
        """
        Process water efficiency analysis request.
        """
        self.log_info(f"Processing water efficiency analysis for field {state.field_id}")

        try:
            # Step 1: Fetch recommendations and actual usage data
            state = await self._fetch_data(state, db)
            if state.error:
                return state

            # Step 2: Calculate efficiency metrics
            state = await self._calculate_metrics(state)
            if state.error:
                return state

            state.step = "complete"
            self.log_info(
                f"Water efficiency analysis complete for field {state.field_id}"
            )

        except Exception as e:
            self.log_error(f"Error processing water efficiency analysis: {e}", exc_info=True)
            state.error = str(e)
            state.step = "error"

        return state

    async def _fetch_data(
        self, state: WaterEfficiencyAgentState, db: AsyncSession
    ) -> WaterEfficiencyAgentState:
        """
        Fetch irrigation recommendations and simulate actual water usage data.
        """
        self.log_debug("Fetching data")
        state.step = "fetch_data"

        try:
            recommendations, _ = await RecommendationService.list_recommendations(
                db=db, field_id=state.field_id, page_size=100  # Fetch up to 100 recs
            )

            for rec in recommendations:
                # Convert recommendation to dict for state
                state.recommendations.append({
                    "action": rec.action,
                    "water_volume_liters": rec.water_saved_liters if rec.action == RecommendationAction.DELAY else 5000, # Simplified
                })

                # Simulate actual irrigation data
                actual_usage = 0
                if rec.action == RecommendationAction.IRRIGATE:
                    # Simulate usage with a +/- 10% variance
                    actual_usage = 5000 * random.uniform(0.9, 1.1)
                elif rec.action == RecommendationAction.DELAY:
                    # Simulate occasional incorrect irrigation
                    if random.random() < 0.1: # 10% chance of irrigating when told not to
                        actual_usage = 1000 * random.uniform(0.5, 1.5)
                
                state.actual_irrigation_data.append({"volume_liters": actual_usage})

        except Exception as e:
            self.log_error(f"Error fetching data for water efficiency agent: {e}", exc_info=True)
            state.error = "Failed to fetch data"

        return state

    async def _calculate_metrics(
        self, state: WaterEfficiencyAgentState
    ) -> WaterEfficiencyAgentState:
        """
        Calculate water efficiency metrics.
        """
        self.log_debug("Calculating metrics")
        state.step = "calculate_metrics"

        state.total_water_recommended = sum(
            rec.get("water_volume_liters") or 0 for rec in state.recommendations
        )
        state.total_water_used = sum(
            usage.get("volume_liters", 0) for usage in state.actual_irrigation_data
        )
        state.water_saved = max(0, state.total_water_recommended - state.total_water_used)

        if state.total_water_recommended > 0:
            efficiency = state.total_water_used / state.total_water_recommended
            state.efficiency_score = 1.0 - abs(1.0 - efficiency)
        else:
            state.efficiency_score = 0.0
            
        # Identify inefficiencies (simple example)
        for rec, usage in zip(state.recommendations, state.actual_irrigation_data):
            if rec["action"] == RecommendationAction.DELAY and usage["volume_liters"] > 0:
                state.inefficiencies.append(
                    f"Irrigated {usage['volume_liters']:.0f}L when recommendation was to delay."
                )
        
        state.water_metrics = {
            "field_id": state.field_id,
            "water_recommended_liters": state.total_water_recommended,
            "water_used_liters": state.total_water_used,
            "water_saved_liters": state.water_saved,
            "efficiency_percent": state.efficiency_score * 100,
            "inefficiencies": state.inefficiencies,
        }

        return state

    async def analyze(
        self,
        db: AsyncSession,
        field_id: UUID,
        time_period: str = "last_30_days",
    ) -> WaterEfficiencyAgentState:
        """
        Analyze water efficiency for a field.
        """
        state = WaterEfficiencyAgentState(field_id=field_id, time_period=time_period)
        return await self.process(state, db)


# Global instance
water_efficiency_agent = WaterEfficiencyAgent()