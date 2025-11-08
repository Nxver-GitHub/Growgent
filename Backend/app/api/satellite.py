"""
API routes for satellite/NDVI data.

Handles endpoints for accessing crop health data from satellite imagery.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.mcp.satellite import satellite_mcp
from app.services.field import FieldService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/satellite", tags=["satellite"])


@router.get(
    "/ndvi",
    response_model=APIResponse,
    summary="Get NDVI data for a field",
    description="Get NDVI (Normalized Difference Vegetation Index) and crop health data from satellite imagery",
)
async def get_ndvi_data(
    field_id: UUID,
    days_back: int = 30,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get NDVI data for a field.

    Args:
        field_id: Field UUID
        days_back: Number of days to look back for historical data (default: 30, max: 365)
        db: Database session

    Returns:
        APIResponse with NDVI data and crop health metrics
    """
    logger.info(f"Getting NDVI data for field: {field_id}, days_back: {days_back}")

    # Validate days_back
    if days_back < 1 or days_back > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days_back must be between 1 and 365",
        )

    try:
        # Get field data
        field = await FieldService.get_field(db=db, field_id=field_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field {field_id} not found",
            )

        # Extract location (simplified - would parse PostGIS geometry in production)
        # For now, use defaults if location not available
        latitude = 38.5  # Default California location
        longitude = -122.5

        if field.location_geom:
            # TODO: Parse PostGIS geometry to extract lat/lon
            # For MVP, using defaults
            pass

        # Get NDVI data
        ndvi_data = await satellite_mcp.get_ndvi(
            latitude=latitude,
            longitude=longitude,
            area_hectares=field.area_hectares,
            days_back=days_back,
        )

        return success_response(
            data=ndvi_data,
            message="NDVI data retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NDVI data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get NDVI data",
        )


@router.get(
    "/crop-health",
    response_model=APIResponse,
    summary="Get crop health summary",
    description="Get comprehensive crop health summary with NDVI, insights, and recommendations",
)
async def get_crop_health_summary(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get crop health summary for a field.

    Args:
        field_id: Field UUID
        db: Database session

    Returns:
        APIResponse with crop health summary including insights and warnings
    """
    logger.info(f"Getting crop health summary for field: {field_id}")

    try:
        # Get field data
        field = await FieldService.get_field(db=db, field_id=field_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field {field_id} not found",
            )

        # Extract location (simplified)
        latitude = 38.5
        longitude = -122.5

        if field.location_geom:
            # TODO: Parse PostGIS geometry
            pass

        # Get crop health summary
        health_summary = await satellite_mcp.get_crop_health_summary(
            field_id=field_id,
            latitude=latitude,
            longitude=longitude,
            crop_type=field.crop_type,
        )

        return success_response(
            data=health_summary,
            message="Crop health summary retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting crop health summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get crop health summary",
        )


@router.get(
    "/fields/{field_id}/ndvi/history",
    response_model=APIResponse,
    summary="Get NDVI historical trend",
    description="Get historical NDVI data points for trend analysis",
)
async def get_ndvi_history(
    field_id: UUID,
    days_back: int = 60,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get historical NDVI data for trend analysis.

    Args:
        field_id: Field UUID
        days_back: Number of days to look back (default: 60, max: 365)
        db: Database session

    Returns:
        APIResponse with historical NDVI data points
    """
    logger.info(f"Getting NDVI history for field: {field_id}, days_back: {days_back}")

    # Validate days_back
    if days_back < 1 or days_back > 365:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="days_back must be between 1 and 365",
        )

    try:
        # Get field data
        field = await FieldService.get_field(db=db, field_id=field_id)
        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field {field_id} not found",
            )

        # Extract location
        latitude = 38.5
        longitude = -122.5

        if field.location_geom:
            # TODO: Parse PostGIS geometry
            pass

        # Get NDVI data with historical trend
        ndvi_data = await satellite_mcp.get_ndvi(
            latitude=latitude,
            longitude=longitude,
            area_hectares=field.area_hectares,
            days_back=days_back,
        )

        # Extract historical data
        historical = ndvi_data.get("historical", {})
        trend_data = {
            "field_id": str(field_id),
            "crop_type": field.crop_type,
            "current_ndvi": ndvi_data["current"]["ndvi"],
            "trend": historical.get("trend", "stable"),
            "data_points": historical.get("data_points", []),
            "comparison": ndvi_data.get("comparison", {}),
        }

        return success_response(
            data=trend_data,
            message="NDVI history retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting NDVI history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get NDVI history",
        )

