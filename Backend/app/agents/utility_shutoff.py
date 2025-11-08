"""
Utility Shutoff Anticipation Agent.

This agent monitors Public Safety Power Shutoff (PSPS) events and
generates alerts or triggers pre-irrigation actions.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.agents.base import AgentState, BaseAgent
from app.mcp import psps_mcp

logger = logging.getLogger(__name__)


class UtilityShutoffAgentState(AgentState):
    """
    State for the Utility Shutoff Anticipation Agent.
    """
    # Input
    field_id: UUID
    location: Dict[str, float]  # {latitude, longitude}

    # Fetched data
    psps_predictions: list[Dict[str, Any]] = []

    # Decision
    alert_generated: bool = False
    pre_irrigation_triggered: bool = False
    alert_message: Optional[str] = None


class UtilityShutoffAnticipationAgent(BaseAgent):
    """
    Utility Shutoff Anticipation Agent.

    Monitors PSPS events and generates alerts.
    """

    def __init__(self) -> None:
        """Initialize Utility Shutoff Anticipation Agent."""
        super().__init__("UtilityShutoffAnticipationAgent")

    async def process(
        self, state: UtilityShutoffAgentState
    ) -> UtilityShutoffAgentState:
        """
        Process utility shutoff analysis request.
        """
        self.log_info(f"Processing utility shutoff analysis for location {state.location}")

        try:
            # Step 1: Fetch PSPS predictions from MCP
            state = await self._fetch_data(state)
            if state.error:
                return state

            # Step 2: Analyze predictions and generate alerts
            state = await self._analyze_predictions(state)
            if state.error:
                return state

            state.step = "complete"
            self.log_info(
                f"Utility shutoff analysis complete for location {state.location}"
            )

        except Exception as e:
            self.log_error(f"Error processing utility shutoff analysis: {e}", exc_info=True)
            state.error = str(e)
            state.step = "error"

        return state

    async def _fetch_data(
        self, state: UtilityShutoffAgentState
    ) -> UtilityShutoffAgentState:
        """
        Fetch PSPS prediction data from the PSPS MCP server.
        """
        self.log_debug("Fetching PSPS data")
        state.step = "fetch_data"

        try:
            state.psps_predictions = await psps_mcp.get_predicted_shutoffs(
                lat=state.location["latitude"],
                lon=state.location["longitude"],
                hours_ahead=48
            )
        except Exception as e:
            self.log_error(f"Error fetching PSPS data: {e}")
            state.error = "Failed to fetch PSPS data from MCP"

        return state

    async def _analyze_predictions(
        self, state: UtilityShutoffAgentState
    ) -> UtilityShutoffAgentState:
        """
        Analyze PSPS predictions and generate alerts.
        """
        self.log_debug("Analyzing PSPS predictions")
        state.step = "analyze_predictions"

        if not state.psps_predictions:
            self.log_info("No PSPS events predicted.")
            return state

        for prediction in state.psps_predictions:
            if prediction.get("confidence", 0) > 0.75:
                state.alert_generated = True
                state.alert_message = (
                    f"High confidence PSPS event predicted for your area. "
                    f"Starts at {prediction.get('predicted_start_time')}."
                )
                # In a real implementation, this would trigger a notification
                # and potentially a pre-irrigation recommendation.
                self.log_info(f"Generated alert: {state.alert_message}")
                break  # For now, only generate one alert

        return state

    async def check_for_shutoffs(
        self,
        field_id: UUID,
        location: Dict[str, float],
    ) -> UtilityShutoffAgentState:
        """
        Check for utility shutoffs for a given location.
        """
        state = UtilityShutoffAgentState(field_id=field_id, location=location)
        return await self.process(state)


# Global instance
utility_shutoff_agent = UtilityShutoffAnticipationAgent()
