"""
Metrics service for calculating water efficiency and impact metrics.

This service calculates water savings, cost savings, and drought stress scores
by comparing fire-adaptive irrigation recommendations against typical baselines.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.field import Field
from app.models.recommendation import Recommendation, AgentType, RecommendationAction
from app.models.sensor_reading import SensorReading
from app.schemas.metrics import WaterMetricsResponse, WaterMetricsSummaryResponse, FireRiskMetricsResponse

logger = logging.getLogger(__name__)

# Typical water usage per hectare per month by crop type (liters)
# These are baseline estimates for California agriculture
# Can be overridden with farmer-provided data later
TYPICAL_WATER_USAGE_LITERS_PER_HECTARE_PER_MONTH: dict[str, float] = {
    "almond": 12000.0,  # ~12,000 L/ha/month for almonds
    "grape": 8000.0,    # ~8,000 L/ha/month for grapes
    "tomato": 10000.0,  # ~10,000 L/ha/month for tomatoes
    "lettuce": 6000.0,  # ~6,000 L/ha/month for lettuce
    "corn": 9000.0,     # ~9,000 L/ha/month for corn
    "wheat": 5000.0,   # ~5,000 L/ha/month for wheat
    "default": 8000.0, # Default baseline if crop type unknown
}

# Water cost per liter in USD (California average, ~$0.001/L)
WATER_COST_PER_LITER_USD: float = 0.001

# Season length in months (typical growing season)
SEASON_LENGTH_MONTHS: float = 6.0


class MetricsService:
    """Service for calculating water efficiency and impact metrics."""

    @staticmethod
    def _get_typical_water_usage(
        crop_type: str,
        area_hectares: float,
        period_months: float = SEASON_LENGTH_MONTHS,
    ) -> float:
        """
        Calculate typical water usage baseline for a crop and area.

        Args:
            crop_type: Crop type (e.g., "almond", "grape")
            area_hectares: Field area in hectares
            period_months: Period length in months (default: season length)

        Returns:
            Typical water usage in liters
        """
        # Normalize crop type to lowercase for lookup
        crop_key = crop_type.lower().strip()

        # Get liters per hectare per month for this crop
        liters_per_ha_per_month = TYPICAL_WATER_USAGE_LITERS_PER_HECTARE_PER_MONTH.get(
            crop_key,
            TYPICAL_WATER_USAGE_LITERS_PER_HECTARE_PER_MONTH["default"],
        )

        # Calculate total typical usage
        typical_liters = liters_per_ha_per_month * area_hectares * period_months

        logger.debug(
            f"Typical water usage: crop={crop_type}, area={area_hectares}ha, "
            f"period={period_months}mo, total={typical_liters:.0f}L"
        )

        return typical_liters

    @staticmethod
    def _calculate_cost_saved(water_saved_liters: float) -> float:
        """
        Calculate cost savings from water saved.

        Args:
            water_saved_liters: Water saved in liters

        Returns:
            Cost savings in USD
        """
        return water_saved_liters * WATER_COST_PER_LITER_USD

    @staticmethod
    async def _calculate_drought_stress_score(
        db: AsyncSession,
        field_id: UUID,
    ) -> float:
        """
        Calculate drought stress score (0-100, lower is better).

        Based on recent sensor readings and irrigation frequency.

        Args:
            db: Database session
            field_id: Field ID

        Returns:
            Drought stress score (0-100, where 0 = no stress, 100 = severe stress)
        """
        # Get most recent sensor reading
        query = (
            select(SensorReading)
            .where(SensorReading.field_id == field_id)
            .order_by(SensorReading.reading_timestamp.desc())
            .limit(1)
        )

        result = await db.execute(query)
        latest_reading = result.scalar_one_or_none()

        if not latest_reading:
            # No sensor data - assume moderate stress (50)
            logger.warning(f"No sensor readings found for field {field_id}, using default stress score")
            return 50.0

        # Calculate stress based on soil moisture
        # Optimal moisture: 40-60%, stress increases below 30%
        moisture = latest_reading.moisture_percent

        if moisture >= 40.0:
            # Good moisture - low stress
            stress_score = max(0.0, 30.0 - (moisture - 40.0) * 0.5)
        elif moisture >= 30.0:
            # Moderate moisture - moderate stress
            stress_score = 30.0 + (40.0 - moisture) * 2.0
        else:
            # Low moisture - high stress
            stress_score = min(100.0, 70.0 + (30.0 - moisture) * 1.5)

        logger.debug(
            f"Drought stress score: field_id={field_id}, moisture={moisture}%, "
            f"stress={stress_score:.1f}"
        )

        return round(stress_score, 1)

    @staticmethod
    async def calculate_water_saved(
        db: AsyncSession,
        field_id: UUID,
        period: str = "season",
    ) -> WaterMetricsResponse:
        """
        Calculate water efficiency metrics for a field.

        Args:
            db: Database session
            field_id: Field ID
            period: Time period ("season", "month", "week", or "all")

        Returns:
            WaterMetricsResponse with all calculated metrics

        Raises:
            ValueError: If field not found
        """
        logger.info(f"Calculating water metrics: field_id={field_id}, period={period}")

        # Get field
        field_query = select(Field).where(Field.id == field_id)
        field_result = await db.execute(field_query)
        field = field_result.scalar_one_or_none()

        if not field:
            raise ValueError(f"Field not found: {field_id}")

        # Determine time range based on period
        now = datetime.now(timezone.utc)
        if period == "season":
            start_date = now - timedelta(days=180)  # ~6 months
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "week":
            start_date = now - timedelta(days=7)
        else:  # "all"
            start_date = datetime.min.replace(tzinfo=timezone.utc)

        # Get all Fire-Adaptive Irrigation recommendations for this field
        recommendations_query = (
            select(Recommendation)
            .where(
                and_(
                    Recommendation.field_id == field_id,
                    Recommendation.agent_type == AgentType.FIRE_ADAPTIVE_IRRIGATION,
                    Recommendation.created_at >= start_date,
                )
            )
            .order_by(Recommendation.created_at)
        )

        recommendations_result = await db.execute(recommendations_query)
        recommendations = list(recommendations_result.scalars().all())

        logger.debug(f"Found {len(recommendations)} recommendations for field {field_id}")

        # Calculate total recommended water
        # For IRRIGATE and PRE_IRRIGATE actions, sum up water_saved_liters if available
        # Otherwise, estimate from typical usage
        water_recommended_liters = 0.0

        for rec in recommendations:
            if rec.action in (RecommendationAction.IRRIGATE, RecommendationAction.PRE_IRRIGATE):
                # If water_saved_liters is set, use it to infer recommended amount
                # Otherwise, estimate based on field area and typical usage
                if rec.water_saved_liters is not None:
                    # Estimate: if saved X liters, recommended = typical - saved
                    # But we need typical first, so we'll calculate it differently
                    # For now, estimate recommended water based on field area
                    # Typical irrigation event: ~10% of monthly usage
                    monthly_typical = MetricsService._get_typical_water_usage(
                        field.crop_type, field.area_hectares, 1.0
                    )
                    water_recommended_liters += monthly_typical * 0.1  # ~10% per event
                else:
                    # Estimate based on field area
                    monthly_typical = MetricsService._get_typical_water_usage(
                        field.crop_type, field.area_hectares, 1.0
                    )
                    water_recommended_liters += monthly_typical * 0.1

        # Calculate typical baseline for the period
        period_months = (
            SEASON_LENGTH_MONTHS
            if period == "season"
            else (30.0 / 30.0 if period == "month" else (7.0 / 30.0 if period == "week" else SEASON_LENGTH_MONTHS))
        )

        water_typical_liters = MetricsService._get_typical_water_usage(
            field.crop_type,
            field.area_hectares,
            period_months,
        )

        # Calculate savings
        water_saved_liters = max(0.0, water_typical_liters - water_recommended_liters)

        # Calculate efficiency percentage
        if water_typical_liters > 0:
            efficiency_percent = (water_saved_liters / water_typical_liters) * 100.0
        else:
            efficiency_percent = 0.0

        # Calculate cost savings
        cost_saved_usd = MetricsService._calculate_cost_saved(water_saved_liters)

        # Calculate drought stress score
        drought_stress_score = await MetricsService._calculate_drought_stress_score(db, field_id)

        logger.info(
            f"Water metrics calculated: field_id={field_id}, "
            f"recommended={water_recommended_liters:.0f}L, "
            f"typical={water_typical_liters:.0f}L, "
            f"saved={water_saved_liters:.0f}L, "
            f"efficiency={efficiency_percent:.1f}%"
        )

        return WaterMetricsResponse(
            field_id=field_id,
            water_recommended_liters=int(water_recommended_liters),
            water_typical_liters=int(water_typical_liters),
            water_saved_liters=int(water_saved_liters),
            efficiency_percent=round(efficiency_percent, 2),
            cost_saved_usd=round(cost_saved_usd, 2),
            drought_stress_score=drought_stress_score,
            last_updated=datetime.now(timezone.utc),
        )

    @staticmethod
    async def calculate_farm_water_summary(
        db: AsyncSession,
        farm_id: str,
    ) -> WaterMetricsSummaryResponse:
        """
        Calculate farm-wide water metrics summary.

        Args:
            db: Database session
            farm_id: Farm ID

        Returns:
            WaterMetricsSummaryResponse with aggregated metrics

        Raises:
            ValueError: If no fields found for farm
        """
        logger.info(f"Calculating farm water summary: farm_id={farm_id}")

        # Get all fields for this farm
        fields_query = select(Field).where(Field.farm_id == farm_id)
        fields_result = await db.execute(fields_query)
        fields = list(fields_result.scalars().all())

        if not fields:
            raise ValueError(f"No fields found for farm: {farm_id}")

        # Aggregate metrics across all fields
        total_water_recommended = 0
        total_water_typical = 0
        total_water_saved = 0
        total_cost_saved = 0.0
        efficiency_sum = 0.0
        field_count = 0

        for field in fields:
            try:
                metrics = await MetricsService.calculate_water_saved(db, field.id, "season")
                total_water_recommended += metrics.water_recommended_liters
                total_water_typical += metrics.water_typical_liters
                total_water_saved += metrics.water_saved_liters
                total_cost_saved += metrics.cost_saved_usd
                efficiency_sum += metrics.efficiency_percent
                field_count += 1
            except Exception as e:
                logger.warning(f"Error calculating metrics for field {field.id}: {e}")
                continue

        # Calculate average efficiency
        average_efficiency = efficiency_sum / field_count if field_count > 0 else 0.0

        logger.info(
            f"Farm summary calculated: farm_id={farm_id}, "
            f"fields={field_count}, "
            f"total_saved={total_water_saved:.0f}L, "
            f"avg_efficiency={average_efficiency:.1f}%"
        )

        return WaterMetricsSummaryResponse(
            farm_id=farm_id,
            total_water_recommended_liters=total_water_recommended,
            total_water_typical_liters=total_water_typical,
            total_water_saved_liters=total_water_saved,
            average_efficiency_percent=round(average_efficiency, 2),
            total_cost_saved_usd=round(total_cost_saved, 2),
            field_count=field_count,
            last_updated=datetime.now(timezone.utc),
        )

    @staticmethod
    async def calculate_fire_risk_metrics(
        db: AsyncSession,
        field_id: UUID,
    ) -> FireRiskMetricsResponse:
        """
        Calculate fire risk reduction metrics for a field.

        Args:
            db: Database session
            field_id: Field ID

        Returns:
            FireRiskMetricsResponse with fire risk metrics

        Raises:
            ValueError: If field not found
        """
        logger.info(f"Calculating fire risk metrics: field_id={field_id}")

        # Get field
        field_query = select(Field).where(Field.id == field_id)
        field_result = await db.execute(field_query)
        field = field_result.scalar_one_or_none()

        if not field:
            raise ValueError(f"Field not found: {field_id}")

        # Get all Fire-Adaptive recommendations that were accepted
        recommendations_query = (
            select(Recommendation)
            .where(
                and_(
                    Recommendation.field_id == field_id,
                    Recommendation.agent_type == AgentType.FIRE_ADAPTIVE_IRRIGATION,
                    Recommendation.accepted == True,
                )
            )
            .order_by(Recommendation.created_at.desc())
        )

        recommendations_result = await db.execute(recommendations_query)
        recommendations = list(recommendations_result.scalars().all())

        # Calculate total fire risk reduction
        total_reduction = 0.0
        for rec in recommendations:
            if rec.fire_risk_reduction_percent is not None:
                total_reduction += rec.fire_risk_reduction_percent

        # Average reduction per recommendation (or total if cumulative)
        # For MVP, we'll use the average of all accepted recommendations
        if recommendations:
            fire_risk_reduction_percent = total_reduction / len(recommendations)
        else:
            fire_risk_reduction_percent = 0.0

        # Determine current fire risk level (simplified - would use actual fire risk data)
        # For MVP, assume LOW if we have good recommendations, MEDIUM otherwise
        if fire_risk_reduction_percent > 20.0:
            current_fire_risk_level = "LOW"
        elif fire_risk_reduction_percent > 10.0:
            current_fire_risk_level = "MEDIUM"
        else:
            current_fire_risk_level = "HIGH"

        logger.info(
            f"Fire risk metrics calculated: field_id={field_id}, "
            f"reduction={fire_risk_reduction_percent:.1f}%, "
            f"level={current_fire_risk_level}, "
            f"recommendations={len(recommendations)}"
        )

        return FireRiskMetricsResponse(
            field_id=field_id,
            fire_risk_reduction_percent=round(fire_risk_reduction_percent, 2),
            current_fire_risk_level=current_fire_risk_level,
            recommendations_applied=len(recommendations),
            last_updated=datetime.now(timezone.utc),
        )

