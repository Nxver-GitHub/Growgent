"""
PSPS Anticipation Agent.

This agent monitors utility shutoff events and generates alerts when fields
are affected by active or predicted Public Safety Power Shutoffs (PSPS).
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import AgentState, BaseAgent
from app.models.field import Field
from app.models.alert import AlertType, AlertSeverity, AgentType
from app.models.recommendation import RecommendationAction, Recommendation
from app.services.psps import PSPSService
from app.services.alert import AlertService
from app.services.geo import GeoService
from app.agents.user_preferences_helper import get_user_preferences_for_field

if TYPE_CHECKING:
    from app.models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


class PSPSAgentState(AgentState):
    """
    State for PSPS Anticipation Agent.

    Tracks PSPS events and affected fields.
    """

    # Input
    field_id: Optional[UUID] = None  # If None, checks all fields
    farm_id: Optional[str] = None  # Optional farm filter

    # Detected events (using dicts instead of Field objects for Pydantic compatibility)
    affected_field_ids: list[UUID] = []  # List of affected field IDs
    affected_field_data: list[dict] = []  # List of shutoff info dicts
    new_events: list[dict] = []  # List of new PSPS events detected
    alerts_created: int = 0  # Number of alerts created


class PSPSAlertAgent(BaseAgent):
    """
    PSPS Anticipation Agent.

    Monitors utility shutoff events and generates alerts for affected fields.
    Tracks seen events to avoid duplicate alerts.
    Uses user preferences for alert settings and pre-irrigation timing.
    """

    # Default PSPS timing thresholds (can be overridden by user preferences)
    DEFAULT_PSPS_WARNING_HOURS = 48  # Hours before shutoff to send warning
    DEFAULT_PSPS_PRE_IRRIGATE_HOURS = 36  # Hours before shutoff to recommend pre-irrigation

    def __init__(self) -> None:
        """Initialize PSPS Anticipation Agent."""
        super().__init__("PSPSAlertAgent")
        self.psps_service = PSPSService()

    async def process(
        self,
        state: PSPSAgentState,
        db: Optional[AsyncSession] = None,
    ) -> PSPSAgentState:
        """
        Process PSPS monitoring and alert generation.

        Args:
            state: Current agent state
            db: Database session

        Returns:
            Updated agent state with detected events and alerts
        """
        if not db:
            state.error = "Database session required"
            return state

        self.log_info(
            f"Processing PSPS monitoring: field_id={state.field_id}, farm_id={state.farm_id}"
        )

        try:
            # Step 1: Find affected fields
            state = await self._find_affected_fields(state, db)
            if state.error:
                return state

            # Step 2: Generate alerts for new events (checks user preferences)
            state = await self._generate_alerts(state, db)
            if state.error:
                return state

            # Step 3: Generate pre-irrigation recommendations if needed (uses user preferences)
            state = await self._check_pre_irrigation(state, db)

            self.log_info(
                f"PSPS monitoring complete: {len(state.affected_field_ids)} fields affected, "
                f"{state.alerts_created} alerts created"
            )

            state.step = "completed"
            return state

        except Exception as e:
            self.log_error(f"Error processing PSPS monitoring: {e}", exc_info=True)
            state.error = str(e)
            state.step = "error"
            return state

    async def _find_affected_fields(
        self,
        state: PSPSAgentState,
        db: AsyncSession,
    ) -> PSPSAgentState:
        """
        Find fields affected by PSPS shutoffs.

        Args:
            state: Current state
            db: Database session

        Returns:
            Updated state with affected fields
        """
        self.log_debug("Finding fields affected by PSPS shutoffs")
        state.step = "find_affected_fields"

        try:
            # Get affected fields using PSPSService
            affected_fields = await self.psps_service.get_affected_fields(
                db, farm_id=state.farm_id
            )

            # Filter by field_id if specified
            if state.field_id:
                affected_fields = [
                    (field, shutoff) for field, shutoff in affected_fields
                    if field.id == state.field_id
                ]

            # Store field IDs and shutoff data separately for Pydantic compatibility
            state.affected_field_ids = [field.id for field, _ in affected_fields]
            state.affected_field_data = [shutoff_info for _, shutoff_info in affected_fields]

            # Identify new events (not seen before)
            for field, shutoff_info in affected_fields:
                event_id = shutoff_info.get("id", "unknown")
                if self.psps_service.is_new_event(event_id):
                    state.new_events.append(shutoff_info)

            self.log_debug(
                f"Found {len(affected_fields)} affected fields, "
                f"{len(state.new_events)} new events"
            )

            return state

        except Exception as e:
            self.log_error(f"Error finding affected fields: {e}")
            state.error = f"Error finding affected fields: {str(e)}"
            return state

    async def _generate_alerts(
        self,
        state: PSPSAgentState,
        db: AsyncSession,
    ) -> PSPSAgentState:
        """
        Generate alerts for affected fields.

        Args:
            state: Current state
            db: Database session

        Returns:
            Updated state with alerts created
        """
        self.log_debug("Generating PSPS alerts")
        state.step = "generate_alerts"

        alerts_created = 0

        # Reconstruct affected_fields list from stored data
        # We need to fetch fields from DB since we can't store them in state
        from sqlalchemy import select
        affected_fields_list = []
        for field_id, shutoff_info in zip(state.affected_field_ids, state.affected_field_data):
            result = await db.execute(select(Field).where(Field.id == field_id))
            field = result.scalar_one_or_none()
            if field:
                affected_fields_list.append((field, shutoff_info))

        for field, shutoff_info in affected_fields_list:
            event_id = shutoff_info.get("id", "unknown")
            status = shutoff_info.get("status", "UNKNOWN")

            # Only create alerts for new events
            if event_id not in [e.get("id") for e in state.new_events]:
                continue

            # Check user preferences for PSPS alerts
            preferences = await get_user_preferences_for_field(db, field.id)
            if preferences and not preferences.psps_alerts_enabled:
                self.log_debug(f"PSPS alerts disabled for field {field.id}, skipping")
                continue

            try:
                # Determine alert type and severity based on status
                if status == "ACTIVE":
                    alert_type = AlertType.PSPS_ACTIVE
                    severity = AlertSeverity.CRITICAL
                    message = self._format_active_alert(field, shutoff_info)
                elif status == "PREDICTED":
                    alert_type = AlertType.PSPS_WARNING
                    severity = AlertSeverity.CRITICAL
                    message = self._format_predicted_alert(field, shutoff_info)
                else:
                    alert_type = AlertType.PSPS_WARNING
                    severity = AlertSeverity.WARNING
                    message = self._format_generic_alert(field, shutoff_info)

                # Create alert
                await AlertService.create_alert(
                    db=db,
                    field_id=field.id,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    agent_type=AgentType.PSPS_ANTICIPATION,
                )

                alerts_created += 1
                self.log_info(
                    f"Created {severity.value} alert for field {field.id}: {event_id}"
                )

            except Exception as e:
                self.log_error(f"Error creating alert for field {field.id}: {e}")

        state.alerts_created = alerts_created
        return state

    def _format_active_alert(self, field: Field, shutoff_info: dict) -> str:
        """Format alert message for active PSPS."""
        utility = shutoff_info.get("utility", "utility")
        start_time = shutoff_info.get("start_time", "unknown")
        end_time = shutoff_info.get("end_time", "unknown")

        return (
            f"⚠️ ACTIVE POWER SHUTOFF: {utility} has shut off power in your area. "
            f"Field '{field.name}' is affected. "
            f"Started: {start_time}, Estimated end: {end_time}. "
            f"Do not attempt irrigation during shutoff."
        )

    def _format_predicted_alert(self, field: Field, shutoff_info: dict) -> str:
        """Format alert message for predicted PSPS."""
        utility = shutoff_info.get("utility", "utility")
        predicted_start = shutoff_info.get("predicted_start_time", "unknown")
        predicted_end = shutoff_info.get("predicted_end_time", "unknown")
        confidence = shutoff_info.get("confidence", 0.0)

        return (
            f"🚨 POWER SHUTOFF PREDICTED: {utility} may shut off power within 48 hours. "
            f"Field '{field.name}' may be affected. "
            f"Predicted start: {predicted_start}, End: {predicted_end}. "
            f"Confidence: {confidence*100:.0f}%. "
            f"Consider pre-irrigating to prepare."
        )

    def _format_generic_alert(self, field: Field, shutoff_info: dict) -> str:
        """Format generic alert message."""
        utility = shutoff_info.get("utility", "utility")
        status = shutoff_info.get("status", "UNKNOWN")

        return (
            f"⚠️ PSPS Event: {utility} has a {status} shutoff event that may affect "
            f"field '{field.name}'. Please monitor for updates."
        )

    async def _check_pre_irrigation(
        self,
        state: PSPSAgentState,
        db: AsyncSession,
    ) -> PSPSAgentState:
        """
        Check if pre-irrigation recommendations are needed.

        Args:
            state: Current state
            db: Database session

        Returns:
            Updated state
        """
        self.log_debug("Checking for pre-irrigation recommendations")
        state.step = "check_pre_irrigation"

        # Reconstruct affected_fields list
        from sqlalchemy import select
        affected_fields_list = []
        for field_id, shutoff_info in zip(state.affected_field_ids, state.affected_field_data):
            result = await db.execute(select(Field).where(Field.id == field_id))
            field = result.scalar_one_or_none()
            if field:
                affected_fields_list.append((field, shutoff_info))

        for field, shutoff_info in affected_fields_list:
            status = shutoff_info.get("status", "")
            if status != "PREDICTED":
                continue

            # Get user preferences for this field
            preferences = await get_user_preferences_for_field(db, field.id)
            
            # Get pre-irrigation hours from preferences or use default
            pre_irrigate_hours = (
                preferences.psps_pre_irrigation_hours
                if preferences and preferences.psps_pre_irrigation_hours
                else self.DEFAULT_PSPS_PRE_IRRIGATE_HOURS
            )

            # Check if shutoff is within pre-irrigation window
            predicted_start_str = shutoff_info.get("predicted_start_time")
            if not predicted_start_str:
                continue

            try:
                predicted_start = datetime.fromisoformat(
                    predicted_start_str.replace("Z", "+00:00")
                )
                hours_until = (predicted_start - datetime.now(timezone.utc)).total_seconds() / 3600

                # If within pre-irrigation window, create recommendation
                if 0 < hours_until <= pre_irrigate_hours:
                    await self._create_pre_irrigation_recommendation(
                        db, field, shutoff_info, hours_until, preferences
                    )
                    self.log_info(
                        f"Created pre-irrigation recommendation for field {field.id}, "
                        f"{hours_until:.1f} hours until PSPS"
                    )

            except (ValueError, TypeError) as e:
                self.log_warning(f"Error parsing predicted start time: {e}")

        return state

    async def _create_pre_irrigation_recommendation(
        self,
        db: AsyncSession,
        field: Field,
        shutoff_info: dict,
        hours_until: float,
        preferences: Optional["UserPreferences"] = None,
    ) -> None:
        """
        Create a pre-irrigation recommendation for PSPS preparation.

        Args:
            db: Database session
            field: Affected field
            shutoff_info: Shutoff information
            hours_until: Hours until shutoff starts
        """
        try:
            # Check if recommendation already exists for this field and PSPS event
            event_id = shutoff_info.get("id", "unknown")
            existing_query = (
                select(Recommendation)
                .where(
                    Recommendation.field_id == field.id,
                    Recommendation.agent_type == AgentType.PSPS_ANTICIPATION,
                    Recommendation.action == RecommendationAction.PRE_IRRIGATE,
                    Recommendation.psps_alert == True,
                )
                .order_by(Recommendation.created_at.desc())
                .limit(1)
            )

            result = await db.execute(existing_query)
            existing = result.scalar_one_or_none()

            # If recent recommendation exists (within last 6 hours), skip
            if existing:
                time_since = (datetime.now(timezone.utc) - existing.created_at).total_seconds() / 3600
                if time_since < 6.0:
                    self.log_debug(
                        f"Recent pre-irrigation recommendation exists for field {field.id}, skipping"
                    )
                    return

            # Check if auto-pre-irrigation is enabled
            auto_pre_irrigate = (
                preferences.psps_auto_pre_irrigate
                if preferences and preferences.psps_auto_pre_irrigate
                else False
            )

            # Create new recommendation
            recommended_timing = datetime.now(timezone.utc) + timedelta(
                hours=max(1.0, hours_until - 12.0)  # Recommend 12h before shutoff
            )

            recommendation = Recommendation(
                field_id=field.id,
                agent_type=AgentType.PSPS_ANTICIPATION,
                action=RecommendationAction.PRE_IRRIGATE,
                title=f"Pre-Irrigate Before PSPS Shutoff",
                reason=(
                    f"Power shutoff predicted in {hours_until:.1f} hours. "
                    f"Pre-irrigate now to ensure crops have adequate water during the shutoff period."
                ),
                recommended_timing=recommended_timing,
                zones_affected=None,  # Could be enhanced with field zone mapping
                confidence=0.85,  # High confidence for PSPS-triggered recommendations
                fire_risk_reduction_percent=None,
                water_saved_liters=None,
                psps_alert=True,
                accepted=False,
            )

            db.add(recommendation)
            await db.flush()

            self.log_info(
                f"Created pre-irrigation recommendation {recommendation.id} for field {field.id}"
            )

        except Exception as e:
            self.log_error(f"Error creating pre-irrigation recommendation: {e}")

    async def monitor_all_fields(
        self,
        db: AsyncSession,
        farm_id: Optional[str] = None,
    ) -> PSPSAgentState:
        """
        Monitor all fields for PSPS events (convenience method).

        Args:
            db: Database session
            farm_id: Optional farm ID to filter fields

        Returns:
            Agent state with monitoring results
        """
        state = PSPSAgentState(farm_id=farm_id)
        return await self.process(state, db)

    async def monitor_field(
        self,
        db: AsyncSession,
        field_id: UUID,
    ) -> PSPSAgentState:
        """
        Monitor a specific field for PSPS events (convenience method).

        Args:
            db: Database session
            field_id: Field ID to monitor

        Returns:
            Agent state with monitoring results
        """
        state = PSPSAgentState(field_id=field_id)
        return await self.process(state, db)


# Singleton instance for easy access
psps_alert_agent = PSPSAlertAgent()

