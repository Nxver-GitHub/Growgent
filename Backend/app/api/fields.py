"""
API routes for field operations.

Handles endpoints for field management and retrieval.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.field import FieldListResponse, FieldResponse
from app.services.field import FieldService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fields", tags=["fields"])


@router.get(
    "",
    response_model=APIResponse,
    summary="List fields",
    description="Get paginated list of fields with latest sensor readings",
)
async def list_fields(
    farm_id: Optional[str] = None,
    crop_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List all fields with optional filtering.

    Args:
        farm_id: Optional farm ID filter
        crop_type: Optional crop type filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        db: Database session

    Returns:
        APIResponse with paginated fields
    """
    logger.info(
        f"Listing fields: farm_id={farm_id}, crop_type={crop_type}, "
        f"page={page}, page_size={page_size}"
    )

    # Validate pagination
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1",
        )
    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 100",
        )

    try:
        fields, total = await FieldService.list_fields(
            db=db,
            farm_id=farm_id,
            crop_type=crop_type,
            page=page,
            page_size=page_size,
            include_latest_sensor=True,
        )

        response_data = FieldListResponse(
            fields=[FieldResponse.model_validate(field) for field in fields],
            total=total,
            page=page,
            page_size=page_size,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error listing fields: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list fields",
        )


@router.get(
    "/{field_id}",
    response_model=APIResponse,
    summary="Get field details",
    description="Get detailed field information including fire risk overlay data",
)
async def get_field(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get detailed field information.

    Args:
        field_id: Field UUID
        db: Database session

    Returns:
        APIResponse with field data
    """
    logger.info(f"Fetching field: id={field_id}")

    try:
        field = await FieldService.get_field(
            db=db, field_id=field_id, include_relations=True
        )

        if not field:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Field {field_id} not found",
            )

        # Get latest sensor reading
        latest_reading = await FieldService.get_latest_sensor_reading(
            db=db, field_id=field_id
        )

        # Get fire risk data (if field has location)
        fire_risk_data = None
        if field.location_geom:
            # TODO: Extract lat/lon from PostGIS geometry
            # For now, use default location
            from app.mcp import fire_risk_mcp

            try:
                fire_risk_data = await fire_risk_mcp.get_fire_risk_zones(
                    latitude=38.5, longitude=-122.5
                )
            except Exception as e:
                logger.warning(f"Error fetching fire risk data: {e}")

        response_data = {
            "field": FieldResponse.model_validate(field).model_dump(),
            "latest_sensor_reading": (
                {
                    "moisture_percent": latest_reading.moisture_percent,
                    "temperature": latest_reading.temperature,
                    "ph": latest_reading.ph,
                    "reading_timestamp": latest_reading.reading_timestamp.isoformat(),
                }
                if latest_reading
                else None
            ),
            "fire_risk_data": fire_risk_data,
        }

        return success_response(data=response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching field: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch field",
        )

