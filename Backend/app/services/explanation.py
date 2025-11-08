"""
Service for generating agent explanations and transparency.

Converts agent state and recommendations into human-readable explanations
with detailed breakdowns of decision factors, data sources, and alternatives.
"""

import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.field import Field
from app.schemas.explanation import (
    AgentExplanation,
    DecisionFactor,
    DataSource,
    AlternativeScenario,
    ConfidenceBreakdown,
)
from app.agents.irrigation import FireAdaptiveIrrigationAgent, IrrigationAgentState
from app.mcp import sensor_mcp, weather_mcp, fire_risk_mcp, psps_mcp

logger = logging.getLogger(__name__)


class ExplanationService:
    """Service for generating agent explanations."""

    @staticmethod
    async def explain_recommendation(
        db: AsyncSession,
        recommendation_id: UUID,
        include_alternatives: bool = True,
        include_data_sources: bool = True,
    ) -> Optional[AgentExplanation]:
        """
        Generate a comprehensive explanation for a recommendation.

        Args:
            db: Database session
            recommendation_id: ID of the recommendation to explain
            include_alternatives: Whether to include alternative scenarios
            include_data_sources: Whether to include detailed data sources

        Returns:
            AgentExplanation or None if recommendation not found
        """
        logger.debug(f"Generating explanation for recommendation {recommendation_id}")

        # Fetch recommendation
        query = select(Recommendation).where(Recommendation.id == recommendation_id)
        result = await db.execute(query)
        recommendation = result.scalar_one_or_none()

        if not recommendation:
            logger.warning(f"Recommendation {recommendation_id} not found")
            return None

        # Fetch field
        field_query = select(Field).where(Field.id == recommendation.field_id)
        field_result = await db.execute(field_query)
        field = field_result.scalar_one_or_none()

        if not field:
            logger.warning(f"Field {recommendation.field_id} not found")
            return None

        # Generate explanation based on agent type
        if recommendation.agent_type == AgentType.FIRE_ADAPTIVE_IRRIGATION:
            return await ExplanationService._explain_irrigation_agent(
                db=db,
                recommendation=recommendation,
                field=field,
                include_alternatives=include_alternatives,
                include_data_sources=include_data_sources,
            )
        else:
            # Generic explanation for other agent types
            return ExplanationService._explain_generic(
                recommendation=recommendation,
                include_alternatives=include_alternatives,
            )

    @staticmethod
    async def _explain_irrigation_agent(
        db: AsyncSession,
        recommendation: Recommendation,
        field: Field,
        include_alternatives: bool,
        include_data_sources: bool,
    ) -> AgentExplanation:
        """Generate explanation for Fire-Adaptive Irrigation Agent."""
        logger.debug("Generating irrigation agent explanation")

        # Reconstruct agent state by fetching current data
        # (In production, we might store agent state, but for MVP we'll reconstruct)
        agent = FireAdaptiveIrrigationAgent()

        # Fetch current data to reconstruct decision context
        data_sources: List[DataSource] = []
        decision_factors: List[DecisionFactor] = []

        # Get sensor data
        sensor_available = False
        sensor_quality = 0.0
        soil_moisture = None
        try:
            latest_reading = await sensor_mcp.get_latest_reading(field.id)
            if latest_reading:
                sensor_available = True
                soil_moisture = latest_reading.get("moisture_percent")
                sensor_quality = 0.9  # Assume good quality if data exists
                if include_data_sources:
                    data_sources.append(
                        DataSource(
                            name="Soil Moisture Sensor",
                            type="IoT Sensor",
                            available=True,
                            quality_score=sensor_quality,
                            last_updated=latest_reading.get("reading_timestamp"),
                            notes=f"Moisture: {soil_moisture:.1f}%",
                        )
                    )
        except Exception as e:
            logger.warning(f"Error fetching sensor data: {e}")

        if not sensor_available and include_data_sources:
            data_sources.append(
                DataSource(
                    name="Soil Moisture Sensor",
                    type="IoT Sensor",
                    available=False,
                    quality_score=0.0,
                    notes="Sensor data not available",
                )
            )

        # Get weather data
        weather_available = False
        weather_quality = 0.0
        if field.location_geom:
            try:
                # Extract lat/lon from geometry (simplified - in production use proper parsing)
                # For now, use default location
                weather_data = await weather_mcp.get_forecast(38.5, -122.5, days=7)
                if weather_data:
                    weather_available = True
                    weather_quality = 0.85
                    if include_data_sources:
                        data_sources.append(
                            DataSource(
                                name="Weather Forecast",
                                type="NOAA/OpenWeather API",
                                available=True,
                                quality_score=weather_quality,
                                notes="7-day forecast available",
                            )
                        )
            except Exception as e:
                logger.warning(f"Error fetching weather data: {e}")

        if not weather_available and include_data_sources:
            data_sources.append(
                DataSource(
                    name="Weather Forecast",
                    type="NOAA/OpenWeather API",
                    available=False,
                    quality_score=0.0,
                    notes="Weather data not available",
                )
            )

        # Build decision factors from recommendation reason
        # Parse the reason to extract key factors
        reason_text = recommendation.reason.lower()

        # Soil moisture factor
        if soil_moisture is not None:
            decision_factors.append(
                DecisionFactor(
                    name="Soil Moisture",
                    value=soil_moisture,
                    unit="%",
                    weight=0.4,
                    impact=(
                        "Critical factor for crop health. "
                        f"Current level: {soil_moisture:.1f}%"
                    ),
                    threshold_met=soil_moisture >= 50.0,
                )
            )

        # Fire risk factor (if mentioned in reason)
        if "fire risk" in reason_text or "fire" in reason_text:
            # Extract fire risk score from reason or use default
            fire_risk_value = 0.7  # Default if not available
            decision_factors.append(
                DecisionFactor(
                    name="Fire Risk",
                    value=fire_risk_value,
                    unit="score (0-1)",
                    weight=0.35,
                    impact="High fire risk requires careful irrigation timing",
                    threshold_met=fire_risk_value >= 0.7,
                )
            )

        # PSPS factor
        if recommendation.psps_alert:
            decision_factors.append(
                DecisionFactor(
                    name="PSPS Prediction",
                    value=1.0,
                    unit="boolean",
                    weight=0.5,
                    impact="Power shutoff predicted - pre-irrigation recommended",
                    threshold_met=True,
                )
            )

        # Generate alternatives
        alternatives: List[AlternativeScenario] = []
        if include_alternatives:
            alternatives = ExplanationService._generate_alternatives(
                recommendation=recommendation
            )

        # Calculate confidence breakdown
        confidence_breakdown = ConfidenceBreakdown(
            data_quality=recommendation.confidence * 0.4,  # Simplified
            decision_certainty=recommendation.confidence * 0.4,
            model_confidence=recommendation.confidence * 0.2,
            overall=recommendation.confidence,
        )

        # Determine urgency
        urgency = "medium"
        if recommendation.psps_alert:
            urgency = "critical"
        elif recommendation.action == RecommendationAction.IRRIGATE:
            urgency = "high"
        elif recommendation.action == RecommendationAction.DELAY:
            urgency = "low"

        # Generate summary
        summary = ExplanationService._generate_summary(recommendation)

        return AgentExplanation(
            recommendation_id=recommendation.id,
            agent_type=recommendation.agent_type,
            action=recommendation.action,
            summary=summary,
            reasoning=recommendation.reason,
            decision_factors=decision_factors,
            data_sources=data_sources if include_data_sources else [],
            confidence_breakdown=confidence_breakdown,
            alternatives_considered=alternatives if include_alternatives else [],
            fire_risk_reduction_percent=recommendation.fire_risk_reduction_percent,
            water_saved_liters=recommendation.water_saved_liters,
            recommended_timing=recommendation.recommended_timing,
            urgency=urgency,
            decision_timestamp=recommendation.created_at,
            data_quality_score=recommendation.confidence,  # Simplified
        )

    @staticmethod
    def _generate_alternatives(
        recommendation: Recommendation,
    ) -> List[AlternativeScenario]:
        """Generate alternative scenarios that were considered."""
        alternatives: List[AlternativeScenario] = []

        current_action = recommendation.action

        # Generate alternatives based on current action
        if current_action == RecommendationAction.IRRIGATE:
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.DELAY,
                    reason="Could delay irrigation if fire risk is moderate",
                    confidence=0.6,
                    why_not_chosen="Crop health takes priority due to low soil moisture",
                )
            )
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.MONITOR,
                    reason="Could monitor if conditions are borderline",
                    confidence=0.4,
                    why_not_chosen="Soil moisture too low to delay further",
                )
            )

        elif current_action == RecommendationAction.DELAY:
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.IRRIGATE,
                    reason="Could irrigate to ensure crop health",
                    confidence=0.5,
                    why_not_chosen="Fire risk is high and soil moisture is sufficient",
                )
            )
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.MONITOR,
                    reason="Could monitor if fire risk is uncertain",
                    confidence=0.3,
                    why_not_chosen="Fire risk is clearly high, delay is safer",
                )
            )

        elif current_action == RecommendationAction.MONITOR:
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.IRRIGATE,
                    reason="Could irrigate proactively",
                    confidence=0.5,
                    why_not_chosen="Conditions are balanced, no immediate need",
                )
            )
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.DELAY,
                    reason="Could delay if fire risk increases",
                    confidence=0.4,
                    why_not_chosen="No high fire risk detected currently",
                )
            )

        elif current_action == RecommendationAction.PRE_IRRIGATE:
            alternatives.append(
                AlternativeScenario(
                    action=RecommendationAction.IRRIGATE,
                    reason="Could irrigate immediately",
                    confidence=0.7,
                    why_not_chosen="PSPS timing requires strategic pre-irrigation",
                )
            )

        return alternatives

    @staticmethod
    def _generate_summary(recommendation: Recommendation) -> str:
        """Generate a high-level summary of the recommendation."""
        action_name = recommendation.action.value.replace("_", " ").title()

        if recommendation.psps_alert:
            return (
                f"{action_name} recommended due to predicted power shutoff. "
                f"This will help prepare the field before power loss."
            )
        elif recommendation.action == RecommendationAction.DELAY:
            return (
                f"{action_name} irrigation recommended to reduce fire risk. "
                f"Current soil moisture levels are sufficient to support this delay."
            )
        elif recommendation.action == RecommendationAction.IRRIGATE:
            return (
                f"{action_name} recommended to protect crop health. "
                f"Current conditions indicate immediate irrigation is needed."
            )
        else:
            return (
                f"{action_name} recommended. Conditions are balanced, "
                f"continuing to monitor for changes."
            )

    @staticmethod
    def _explain_generic(
        recommendation: Recommendation,
        include_alternatives: bool,
    ) -> AgentExplanation:
        """Generate generic explanation for non-irrigation agents."""
        return AgentExplanation(
            recommendation_id=recommendation.id,
            agent_type=recommendation.agent_type,
            action=recommendation.action,
            summary=recommendation.reason[:200],
            reasoning=recommendation.reason,
            decision_factors=[],
            data_sources=[],
            confidence_breakdown=ConfidenceBreakdown(
                data_quality=recommendation.confidence * 0.5,
                decision_certainty=recommendation.confidence * 0.3,
                model_confidence=recommendation.confidence * 0.2,
                overall=recommendation.confidence,
            ),
            alternatives_considered=[],
            fire_risk_reduction_percent=recommendation.fire_risk_reduction_percent,
            water_saved_liters=recommendation.water_saved_liters,
            recommended_timing=recommendation.recommended_timing,
            urgency="medium",
            decision_timestamp=recommendation.created_at,
            data_quality_score=recommendation.confidence,
        )

