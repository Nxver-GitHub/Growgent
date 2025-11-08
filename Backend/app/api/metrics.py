"""
API routes for metrics operations.

Handles endpoints for water efficiency metrics, fire risk metrics, and summaries.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.metrics import (
    WaterMetricsResponse,
    WaterMetricsSummaryResponse,
    FireRiskMetricsResponse,
)
from app.services.metrics import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get(
    "/water",
    response_model=APIResponse,
    summary="Get water metrics for field",
    description="Get water efficiency metrics for a specific field",
)
async def get_water_metrics(
    field_id: UUID,
    period: str = "season",
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get water efficiency metrics for a field.

    Args:
        field_id: Field UUID
        period: Time period ("season", "month", "week", or "all")
        db: Database session

    Returns:
        APIResponse with water metrics
    """
    logger.info(f"Getting water metrics: field_id={field_id}, period={period}")

    # Validate period
    valid_periods = ["season", "month", "week", "all"]
    if period not in valid_periods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Period must be one of: {', '.join(valid_periods)}",
        )

    try:
        metrics = await MetricsService.calculate_water_saved(
            db=db,
            field_id=field_id,
            period=period,
        )

        return success_response(
            data=metrics.model_dump(),
            message="Water metrics calculated successfully",
        )

    except ValueError as e:
        logger.error(f"Error getting water metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting water metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate water metrics",
        )


@router.get(
    "/water/summary",
    response_model=APIResponse,
    summary="Get farm-wide water metrics summary",
    description="Get aggregated water metrics across all fields in a farm",
)
async def get_water_summary(
    farm_id: str,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get farm-wide water metrics summary.

    Args:
        farm_id: Farm ID
        db: Database session

    Returns:
        APIResponse with farm-wide water metrics summary
    """
    logger.info(f"Getting water summary: farm_id={farm_id}")

    try:
        summary = await MetricsService.calculate_farm_water_summary(
            db=db,
            farm_id=farm_id,
        )

        return success_response(
            data=summary.model_dump(),
            message="Water summary calculated successfully",
        )

    except ValueError as e:
        logger.error(f"Error getting water summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting water summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate water summary",
        )


@router.get(
    "/fire-risk",
    response_model=APIResponse,
    summary="Get fire risk metrics for field",
    description="Get fire risk reduction metrics for a specific field",
)
async def get_fire_risk_metrics(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get fire risk reduction metrics for a field.

    Args:
        field_id: Field UUID
        db: Database session

    Returns:
        APIResponse with fire risk metrics
    """
    logger.info(f"Getting fire risk metrics: field_id={field_id}")

    try:
        metrics = await MetricsService.calculate_fire_risk_metrics(
            db=db,
            field_id=field_id,
        )

        return success_response(
            data=metrics.model_dump(),
            message="Fire risk metrics calculated successfully",
        )

    except ValueError as e:
        logger.error(f"Error getting fire risk metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error getting fire risk metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate fire risk metrics",
        )

