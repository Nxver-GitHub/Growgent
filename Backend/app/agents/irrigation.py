"""
Fire-Adaptive Irrigation Agent.

This agent makes irrigation recommendations that balance crop health
with wildfire risk, considering PSPS events and environmental conditions.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentState, BaseAgent
from app.mcp import fire_risk_mcp, psps_mcp, sensor_mcp, weather_mcp, satellite_mcp
from app.models.field import Field
from app.models.recommendation import AgentType, RecommendationAction

logger = logging.getLogger(__name__)


class IrrigationAgentState(AgentState):
    """
    State for Fire-Adaptive Irrigation Agent.

    Tracks all data needed for decision-making throughout the agent workflow.
    """

    # Input
    field_id: UUID
    crop_stage: Optional[str] = None  # e.g., "seedling", "vegetative", "flowering", "maturity"

    # Fetched data
    current_soil_moisture: Optional[float] = None  # Percentage (0-100)
    weather_forecast: Optional[Dict[str, Any]] = None
    fire_risk_data: Optional[Dict[str, Any]] = None
    psps_predictions: Optional[list[Dict[str, Any]]] = None
    field_location: Optional[Dict[str, float]] = None  # {latitude, longitude}
    ndvi_data: Optional[Dict[str, Any]] = None  # NDVI and crop health data

    # Calculated values
    water_need: Optional[float] = None  # Calculated water need
    fire_risk_score: Optional[float] = None  # 0.0 to 1.0
    drought_risk_score: Optional[float] = None  # 0.0 to 1.0

    # Decision
    recommended_action: Optional[RecommendationAction] = None
    recommended_timing: Optional[datetime] = None
    zones_affected: Optional[list[str]] = None
    confidence: Optional[float] = None  # 0.0 to 1.0
    fire_risk_reduction_percent: Optional[float] = None
    water_saved_liters: Optional[float] = None
    psps_alert: bool = False

    # Metadata
    reasoning: Optional[str] = None
    data_quality_score: Optional[float] = None  # 0.0 to 1.0


class FireAdaptiveIrrigationAgent(BaseAgent):
    """
    Fire-Adaptive Irrigation Agent.

    Makes irrigation recommendations that balance crop health with wildfire risk.
    Uses rule-based logic (no ML for MVP).
    """

    # Decision thresholds (configurable)
    SOIL_MOISTURE_LOW_THRESHOLD = 30.0  # Below this, crop is at risk
    SOIL_MOISTURE_SUFFICIENT_THRESHOLD = 50.0  # Above this, crop is safe
    FIRE_RISK_HIGH_THRESHOLD = 0.7  # Above this, fire risk is high
    DROUGHT_RISK_HIGH_THRESHOLD = 0.6  # Above this, drought risk is high
    PSPS_PRE_IRRIGATE_HOURS = 36  # Hours before PSPS to pre-irrigate

    # Weighting factors (50/50 balance for MVP)
    FIRE_RISK_WEIGHT = 0.5
    CROP_HEALTH_WEIGHT = 0.5

    def __init__(self) -> None:
        """Initialize Fire-Adaptive Irrigation Agent."""
        super().__init__("FireAdaptiveIrrigationAgent")

    async def process(
        self, state: IrrigationAgentState, db: Optional[AsyncSession] = None
    ) -> IrrigationAgentState:
        """
        Process irrigation recommendation request.

        Args:
            state: Current agent state with field_id
            db: Optional database session for fetching field data

        Returns:
            Updated state with recommendation
        """
        self.log_info(f"Processing recommendation for field {state.field_id}")

        try:
            # Step 1: Fetch field data
            state = await self._fetch_field_data(state, db)
            if state.error:
                return state

            # Step 2: Fetch external data via MCP servers
            state = await self._fetch_external_data(state)
            if state.error:
                return state

            # Step 3: Calculate water need and risk scores
            state = await self._calculate_metrics(state)
            if state.error:
                return state

            # Step 4: Make decision
            state = await self._make_decision(state)
            if state.error:
                return state

            # Step 5: Calculate impact metrics
            state = await self._calculate_impact(state)

            state.step = "complete"
            self.log_info(
                f"Recommendation complete: {state.recommended_action} "
                f"(confidence: {state.confidence})"
            )

        except Exception as e:
            self.log_error(f"Error processing recommendation: {e}", exc_info=True)
            state.error = str(e)
            state.step = "error"

        return state

    async def _fetch_field_data(
        self, state: IrrigationAgentState, db: Optional[AsyncSession] = None
    ) -> IrrigationAgentState:
        """
        Fetch field data from database.

        Args:
            state: Current state
            db: Optional database session (if not provided, uses defaults)

        Returns:
            Updated state with field data
        """
        self.log_debug("Fetching field data")
        state.step = "fetch_field_data"

        if db:
            try:
                result = await db.execute(
                    select(Field).where(Field.id == state.field_id)
                )
                field = result.scalar_one_or_none()

                if field:
                    # Extract location from PostGIS geometry
                    # For MVP, use default if location not available
                    if field.location_geom:
                        # TODO: Parse PostGIS geometry to get lat/lon
                        # For now, use defaults
                        state.field_location = {"latitude": 38.5, "longitude": -122.5}
                    else:
                        state.field_location = {"latitude": 38.5, "longitude": -122.5}

                    # Use crop_type to infer stage (simplified for MVP)
                    state.crop_stage = "vegetative"  # Default
                    self.log_debug(f"Field found: {field.name}, crop: {field.crop_type}")
                else:
                    self.log_warning(f"Field {state.field_id} not found in database")
                    state.field_location = {"latitude": 38.5, "longitude": -122.5}
                    state.crop_stage = "vegetative"
            except Exception as e:
                self.log_error(f"Error fetching field data: {e}")
                state.field_location = {"latitude": 38.5, "longitude": -122.5}
                state.crop_stage = "vegetative"
        else:
            # No database session, use defaults
            state.field_location = {"latitude": 38.5, "longitude": -122.5}
            state.crop_stage = "vegetative"

        return state

    async def _fetch_external_data(
        self, state: IrrigationAgentState
    ) -> IrrigationAgentState:
        """
        Fetch external data from MCP servers.

        Args:
            state: Current state

        Returns:
            Updated state with external data
        """
        self.log_debug("Fetching external data from MCP servers")
        state.step = "fetch_external_data"

        if not state.field_location:
            state.error = "Field location not available"
            return state

        lat = state.field_location["latitude"]
        lon = state.field_location["longitude"]

        try:
            # Fetch sensor readings (latest)
            latest_reading = await sensor_mcp.get_latest_reading(state.field_id)
            if latest_reading:
                state.current_soil_moisture = latest_reading.get("moisture_percent")

            # Fetch weather forecast
            state.weather_forecast = await weather_mcp.get_forecast(lat, lon, days=7)

            # Fetch fire risk zones
            state.fire_risk_data = await fire_risk_mcp.get_fire_risk_zones(lat, lon)

            # Fetch PSPS predictions (48 hours ahead)
            state.psps_predictions = await psps_mcp.get_predicted_shutoffs(
                lat, lon, hours_ahead=48
            )

            # Fetch NDVI and crop health data
            if state.field_location:
                state.ndvi_data = await satellite_mcp.get_ndvi(
                    lat, lon, days_back=30
                )

            self.log_debug("External data fetched successfully")

        except Exception as e:
            self.log_error(f"Error fetching external data: {e}")
            state.error = f"Error fetching external data: {str(e)}"

        return state

    async def _calculate_metrics(
        self, state: IrrigationAgentState
    ) -> IrrigationAgentState:
        """
        Calculate water need and risk scores.

        Args:
            state: Current state

        Returns:
            Updated state with calculated metrics
        """
        self.log_debug("Calculating metrics")
        state.step = "calculate_metrics"

        # Calculate water need based on crop stage and heat stress
        state.water_need = self._calculate_water_need(
            state.crop_stage, state.weather_forecast
        )

        # Calculate fire risk score
        state.fire_risk_score = self._calculate_fire_risk_score(state.fire_risk_data)

        # Calculate drought risk score
        state.drought_risk_score = self._calculate_drought_risk_score(
            state.current_soil_moisture, state.weather_forecast
        )

        # Calculate data quality score
        state.data_quality_score = self._calculate_data_quality_score(state)

        return state

    def _calculate_water_need(
        self, crop_stage: Optional[str], weather_forecast: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate water need based on crop stage and weather.

        Args:
            crop_stage: Current crop growth stage
            weather_forecast: Weather forecast data

        Returns:
            Water need score (0.0 to 1.0)
        """
        # Base water need by crop stage
        stage_multipliers = {
            "seedling": 0.6,
            "vegetative": 0.8,
            "flowering": 1.0,  # Highest need
            "maturity": 0.7,
        }
        base_need = stage_multipliers.get(crop_stage or "vegetative", 0.8)

        # Adjust for heat stress
        if weather_forecast and "current" in weather_forecast:
            temp = weather_forecast["current"].get("temperature", 20.0)
            # Increase need if temperature is high
            if temp > 30:
                base_need *= 1.3
            elif temp > 25:
                base_need *= 1.1

        return min(1.0, base_need)

    def _calculate_fire_risk_score(
        self, fire_risk_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate fire risk score from fire risk data.

        Args:
            fire_risk_data: Fire risk zone data

        Returns:
            Fire risk score (0.0 to 1.0)
        """
        if not fire_risk_data or "zones" not in fire_risk_data:
            return 0.5  # Default moderate risk if no data

        zones = fire_risk_data.get("zones", [])
        if not zones:
            return 0.5

        # Use highest risk zone
        max_risk = 0.0
        for zone in zones:
            risk_score = zone.get("risk_score", 0.0)
            max_risk = max(max_risk, risk_score)

        return max_risk

    def _calculate_drought_risk_score(
        self,
        soil_moisture: Optional[float],
        weather_forecast: Optional[Dict[str, Any]],
    ) -> float:
        """
        Calculate drought risk score.

        Args:
            soil_moisture: Current soil moisture percentage
            weather_forecast: Weather forecast data

        Returns:
            Drought risk score (0.0 to 1.0)
        """
        risk = 0.0

        # Soil moisture component
        if soil_moisture is not None:
            if soil_moisture < self.SOIL_MOISTURE_LOW_THRESHOLD:
                risk += 0.7  # High drought risk
            elif soil_moisture < self.SOIL_MOISTURE_SUFFICIENT_THRESHOLD:
                risk += 0.4  # Moderate risk
            else:
                risk += 0.1  # Low risk

        # Weather component (precipitation forecast)
        if weather_forecast and "forecast" in weather_forecast:
            forecast = weather_forecast["forecast"]
            # Check next 3 days for precipitation
            total_precip = sum(
                day.get("precipitation", 0) for day in forecast[:3]
            )
            if total_precip < 5.0:  # Less than 5mm in 3 days
                risk += 0.3

        return min(1.0, risk)

    def _calculate_data_quality_score(
        self, state: IrrigationAgentState
    ) -> float:
        """
        Calculate data quality score based on available data.

        Args:
            state: Current state

        Returns:
            Data quality score (0.0 to 1.0)
        """
        score = 0.0
        max_score = 6.0  # Updated to include NDVI

        if state.current_soil_moisture is not None:
            score += 1.0
        if state.weather_forecast:
            score += 1.0
        if state.fire_risk_data:
            score += 1.0
        if state.psps_predictions is not None:
            score += 1.0
        if state.field_location:
            score += 1.0
        if state.ndvi_data:
            score += 1.0  # NDVI adds to data quality

        return score / max_score

    async def _make_decision(
        self, state: IrrigationAgentState
    ) -> IrrigationAgentState:
        """
        Make irrigation decision based on calculated metrics.

        Decision logic:
        1. IF PSPS predicted in 48h → PRE_IRRIGATE
        2. IF fire_risk_high AND soil_moisture_sufficient → DELAY
        3. IF soil_moisture_low OR drought_risk_high → IRRIGATE
        4. ELSE → MONITOR

        Args:
            state: Current state

        Returns:
            Updated state with decision
        """
        self.log_debug("Making irrigation decision")
        state.step = "make_decision"

        # Check for PSPS prediction
        if state.psps_predictions:
            for psps in state.psps_predictions:
                predicted_time_str = psps.get("predicted_start_time")
                if predicted_time_str:
                    try:
                        predicted_time = datetime.fromisoformat(
                            predicted_time_str.replace("Z", "+00:00")
                        )
                        hours_until = (predicted_time - datetime.now()).total_seconds() / 3600

                        if 0 < hours_until <= self.PSPS_PRE_IRRIGATE_HOURS:
                            state.recommended_action = RecommendationAction.PRE_IRRIGATE
                            state.recommended_timing = (
                                datetime.now() + timedelta(hours=hours_until - 12)
                            )
                            state.psps_alert = True
                            state.reasoning = (
                                f"PSPS predicted in {hours_until:.1f} hours. "
                                "Pre-irrigating to prepare for power shutoff."
                            )
                            self.log_info("PSPS detected, recommending PRE_IRRIGATE")
                            return state
                    except (ValueError, TypeError) as e:
                        self.log_warning(f"Error parsing PSPS time: {e}")

        # Check fire risk vs crop health
        fire_risk_high = (
            state.fire_risk_score is not None
            and state.fire_risk_score >= self.FIRE_RISK_HIGH_THRESHOLD
        )
        soil_moisture_sufficient = (
            state.current_soil_moisture is not None
            and state.current_soil_moisture >= self.SOIL_MOISTURE_SUFFICIENT_THRESHOLD
        )
        soil_moisture_low = (
            state.current_soil_moisture is not None
            and state.current_soil_moisture < self.SOIL_MOISTURE_LOW_THRESHOLD
        )
        drought_risk_high = (
            state.drought_risk_score is not None
            and state.drought_risk_score >= self.DROUGHT_RISK_HIGH_THRESHOLD
        )

        # Check crop health from NDVI
        crop_health_poor = False
        if state.ndvi_data and "current" in state.ndvi_data:
            current_ndvi = state.ndvi_data["current"].get("ndvi", 0.5)
            health_status = state.ndvi_data["current"].get("health_status", "fair")
            if health_status == "poor" or current_ndvi < 0.3:
                crop_health_poor = True
                self.log_info(f"Poor crop health detected (NDVI: {current_ndvi:.2f})")

        # Decision logic
        if fire_risk_high and soil_moisture_sufficient:
            state.recommended_action = RecommendationAction.DELAY
            state.recommended_timing = datetime.now() + timedelta(hours=24)
            state.reasoning = (
                f"Fire risk is high ({state.fire_risk_score:.2f}) and soil moisture "
                f"is sufficient ({state.current_soil_moisture:.1f}%). "
                "Delaying irrigation to reduce fuel moisture."
            )
            self.log_info("High fire risk + sufficient moisture → DELAY")

        elif soil_moisture_low or drought_risk_high or crop_health_poor:
            state.recommended_action = RecommendationAction.IRRIGATE
            state.recommended_timing = datetime.now() + timedelta(hours=6)
            reasons = []
            if soil_moisture_low:
                reasons.append(f"soil moisture is low ({state.current_soil_moisture:.1f}%)")
            if drought_risk_high:
                reasons.append(f"drought risk is high ({state.drought_risk_score:.2f})")
            if crop_health_poor:
                ndvi_val = state.ndvi_data["current"]["ndvi"] if state.ndvi_data else None
                reasons.append(f"crop health is poor (NDVI: {ndvi_val:.2f})" if ndvi_val else "crop health is poor")
            state.reasoning = f"{', '.join(reasons)}. Irrigating to protect crop health."
            self.log_info("Low moisture, high drought risk, or poor crop health → IRRIGATE")

        else:
            state.recommended_action = RecommendationAction.MONITOR
            state.recommended_timing = datetime.now() + timedelta(hours=12)
            state.reasoning = (
                "Conditions are balanced. Monitoring and will reassess in 12 hours."
            )
            self.log_info("Balanced conditions → MONITOR")

        # Default zones (can be enhanced with field zone mapping)
        state.zones_affected = ["zone-1", "zone-2"]

        return state

    async def _calculate_impact(
        self, state: IrrigationAgentState
    ) -> IrrigationAgentState:
        """
        Calculate impact metrics for the recommendation.

        Args:
            state: Current state

        Returns:
            Updated state with impact metrics
        """
        self.log_debug("Calculating impact metrics")
        state.step = "calculate_impact"

        # Calculate confidence based on data quality and decision certainty
        state.confidence = self._calculate_confidence(state)

        # Calculate fire risk reduction (if DELAY action)
        if state.recommended_action == RecommendationAction.DELAY:
            # Estimate fire risk reduction from delaying irrigation
            state.fire_risk_reduction_percent = min(
                15.0, state.fire_risk_score * 20.0 if state.fire_risk_score else 0.0
            )
        else:
            state.fire_risk_reduction_percent = 0.0

        # Calculate water saved (if DELAY action)
        if state.recommended_action == RecommendationAction.DELAY:
            # Estimate water saved by delaying (assume 5000L per irrigation)
            state.water_saved_liters = 5000.0
        else:
            state.water_saved_liters = 0.0

        return state

    def _calculate_confidence(self, state: IrrigationAgentState) -> float:
        """
        Calculate confidence score for the recommendation.

        Args:
            state: Current state

        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from data quality
        base_confidence = state.data_quality_score or 0.5

        # Adjust based on decision clarity
        if state.recommended_action == RecommendationAction.PRE_IRRIGATE:
            # High confidence for PSPS-triggered decisions
            return min(1.0, base_confidence + 0.3)

        # Check if decision is clear-cut
        fire_risk_high = (
            state.fire_risk_score is not None
            and state.fire_risk_score >= self.FIRE_RISK_HIGH_THRESHOLD
        )
        soil_moisture_low = (
            state.current_soil_moisture is not None
            and state.current_soil_moisture < self.SOIL_MOISTURE_LOW_THRESHOLD
        )

        if (fire_risk_high and state.current_soil_moisture) or soil_moisture_low:
            # Clear decision → higher confidence
            return min(1.0, base_confidence + 0.2)

        # Ambiguous decision → lower confidence
        return max(0.5, base_confidence - 0.1)

    async def recommend(
        self,
        field_id: UUID,
        crop_stage: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> IrrigationAgentState:
        """
        Generate irrigation recommendation for a field.

        Args:
            field_id: Field UUID
            crop_stage: Optional crop growth stage
            db: Optional database session

        Returns:
            Agent state with recommendation
        """
        state = IrrigationAgentState(field_id=field_id, crop_stage=crop_stage)
        return await self.process(state, db)


# Global instance
fire_adaptive_irrigation_agent = FireAdaptiveIrrigationAgent()

