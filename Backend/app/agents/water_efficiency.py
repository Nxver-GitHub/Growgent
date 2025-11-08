"""
Water Efficiency Agent.

This agent tracks and measures water savings from fire-adaptive irrigation
recommendations by comparing recommended usage against typical baselines.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentState, BaseAgent
from app.models.recommendation import AgentType, RecommendationAction
from app.services.metrics import MetricsService
from app.services.alert import AlertService
from app.models.alert import AlertType, AlertSeverity
from app.schemas.metrics import WaterMetricsResponse

logger = logging.getLogger(__name__)


class WaterEfficiencyAgentState(AgentState):
    """
    State for Water Efficiency Agent.

    Tracks water metrics and savings calculations.
    """

    # Input
    field_id: UUID

    # Calculated metrics
    water_metrics: Optional[WaterMetricsResponse] = None
    milestone_reached: bool = False  # True if significant milestone (e.g., 1000L saved)
    last_milestone_alerted: Optional[float] = None  # Last milestone value we alerted for


class WaterEfficiencyAgent(BaseAgent):
    """
    Water Efficiency Agent.

    Calculates water savings from fire-adaptive irrigation recommendations
    and generates milestone alerts when significant savings are achieved.
    """

    # Milestone thresholds (liters saved)
    MILESTONE_1000L = 1000.0
    MILESTONE_5000L = 5000.0
    MILESTONE_10000L = 10000.0
    MILESTONE_25000L = 25000.0

    def __init__(self) -> None:
        """Initialize Water Efficiency Agent."""
        super().__init__("WaterEfficiencyAgent")

    async def process(
        self,
        state: WaterEfficiencyAgentState,
        db: Optional[AsyncSession] = None,
    ) -> WaterEfficiencyAgentState:
        """
        Process water efficiency calculations.

        Args:
            state: Current agent state
            db: Database session

        Returns:
            Updated agent state with calculated metrics
        """
        if not db:
            state.error = "Database session required"
            return state

        self.log_info(f"Processing water efficiency for field: {state.field_id}")

        try:
            # Calculate water metrics using MetricsService
            state.water_metrics = await MetricsService.calculate_water_saved(
                db, state.field_id, period="season"
            )

            # Check for milestones and create alerts if needed
            await self._check_milestones(db, state)

            self.log_info(
                f"Water efficiency calculated: field_id={state.field_id}, "
                f"saved={state.water_metrics.water_saved_liters}L, "
                f"efficiency={state.water_metrics.efficiency_percent:.1f}%"
            )

            state.step = "completed"
            return state

        except Exception as e:
            self.log_error(f"Error processing water efficiency: {e}", exc_info=True)
            state.error = str(e)
            state.step = "error"
            return state

    async def _check_milestones(
        self,
        db: AsyncSession,
        state: WaterEfficiencyAgentState,
    ) -> None:
        """
        Check if water savings milestones have been reached and create alerts.

        Args:
            db: Database session
            state: Agent state with calculated metrics
        """
        if not state.water_metrics:
            return

        water_saved = float(state.water_metrics.water_saved_liters)

        # Determine which milestone was reached
        milestone_value = None
        milestone_message = None

        if water_saved >= self.MILESTONE_25000L and (
            state.last_milestone_alerted is None
            or state.last_milestone_alerted < self.MILESTONE_25000L
        ):
            milestone_value = self.MILESTONE_25000L
            milestone_message = (
                f"🎉 Amazing! You've saved over 25,000 liters of water this season! "
                f"Total savings: {water_saved:,.0f}L (${state.water_metrics.cost_saved_usd:.2f})"
            )
        elif water_saved >= self.MILESTONE_10000L and (
            state.last_milestone_alerted is None
            or state.last_milestone_alerted < self.MILESTONE_10000L
        ):
            milestone_value = self.MILESTONE_10000L
            milestone_message = (
                f"Excellent! You've saved over 10,000 liters of water this season! "
                f"Total savings: {water_saved:,.0f}L (${state.water_metrics.cost_saved_usd:.2f})"
            )
        elif water_saved >= self.MILESTONE_5000L and (
            state.last_milestone_alerted is None
            or state.last_milestone_alerted < self.MILESTONE_5000L
        ):
            milestone_value = self.MILESTONE_5000L
            milestone_message = (
                f"Great progress! You've saved over 5,000 liters of water this season! "
                f"Total savings: {water_saved:,.0f}L (${state.water_metrics.cost_saved_usd:.2f})"
            )
        elif water_saved >= self.MILESTONE_1000L and (
            state.last_milestone_alerted is None
            or state.last_milestone_alerted < self.MILESTONE_1000L
        ):
            milestone_value = self.MILESTONE_1000L
            milestone_message = (
                f"Congratulations! You've saved over 1,000 liters of water this season! "
                f"Total savings: {water_saved:,.0f}L (${state.water_metrics.cost_saved_usd:.2f})"
            )

        # Create alert if milestone reached
        if milestone_value and milestone_message:
            try:
                await AlertService.create_alert(
                    db=db,
                    field_id=state.field_id,
                    alert_type=AlertType.WATER_SAVED_MILESTONE,
                    severity=AlertSeverity.INFO,
                    message=milestone_message,
                    agent_type=AgentType.WATER_EFFICIENCY,
                )
                state.milestone_reached = True
                state.last_milestone_alerted = milestone_value
                self.log_info(
                    f"Created milestone alert: {milestone_value}L saved for field {state.field_id}"
                )
            except Exception as e:
                self.log_error(f"Error creating milestone alert: {e}")

    async def calculate_for_field(
        self,
        db: AsyncSession,
        field_id: UUID,
    ) -> WaterMetricsResponse:
        """
        Calculate water efficiency metrics for a field (convenience method).

        Args:
            db: Database session
            field_id: Field ID

        Returns:
            WaterMetricsResponse with calculated metrics
        """
        state = WaterEfficiencyAgentState(field_id=field_id)
        state = await self.process(state, db)

        if state.error:
            raise ValueError(f"Error calculating water efficiency: {state.error}")

        if not state.water_metrics:
            raise ValueError("Water metrics not calculated")

        return state.water_metrics


# Singleton instance for easy access
water_efficiency_agent = WaterEfficiencyAgent()

