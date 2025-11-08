"""
API routes for zone operations.

Handles CRUD endpoints for risk zone management with GeoJSON geometry.
"""

import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.models.zone import ZoneType, RiskLevel
from app.schemas.zone import (
    ZoneCreate,
    ZoneUpdate,
    ZoneResponse,
    ZoneListResponse,
)
from app.services.zone import ZoneService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/zones", tags=["zones"])


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create zone",
    description="Create a new risk zone with GeoJSON geometry",
)
async def create_zone(
    zone_data: ZoneCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Create a new risk zone.

    Args:
        zone_data: Zone creation data with GeoJSON geometry
        db: Database session

    Returns:
        APIResponse with created zone
    """
    logger.info(f"Creating zone: name={zone_data.name}, type={zone_data.zone_type}")

    try:
        zone = await ZoneService.create_zone(
            db=db,
            name=zone_data.name,
            description=zone_data.description,
            zone_type=zone_data.zone_type,
            risk_level=zone_data.risk_level,
            geometry=zone_data.geometry,
            field_id=zone_data.field_id,
            farm_id=zone_data.farm_id,
            extra_metadata=zone_data.extra_metadata,
        )

        # Convert to response format with GeoJSON
        zone_dict = ZoneService._zone_to_dict(zone)
        response_data = ZoneResponse.model_validate(zone_dict)

        return success_response(data=response_data.model_dump(), status_code=status.HTTP_201_CREATED)

    except ValueError as e:
        logger.error(f"Validation error creating zone: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create zone",
        )


@router.get(
    "",
    response_model=APIResponse,
    summary="List zones",
    description="Get paginated list of zones with optional filtering",
)
async def list_zones(
    zone_type: Optional[ZoneType] = None,
    risk_level: Optional[RiskLevel] = None,
    field_id: Optional[str] = None,
    farm_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List all zones with optional filtering.

    Args:
        zone_type: Optional zone type filter
        risk_level: Optional risk level filter
        field_id: Optional field ID filter
        farm_id: Optional farm ID filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        db: Database session

    Returns:
        APIResponse with paginated zones
    """
    logger.info(
        f"Listing zones: type={zone_type}, risk={risk_level}, "
        f"field_id={field_id}, farm_id={farm_id}, page={page}, page_size={page_size}"
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
        zones, total = await ZoneService.list_zones(
            db=db,
            zone_type=zone_type,
            risk_level=risk_level,
            field_id=field_id,
            farm_id=farm_id,
            page=page,
            page_size=page_size,
        )

        # Convert zones to response format with GeoJSON
        zones_data = [ZoneResponse.model_validate(ZoneService._zone_to_dict(zone)) for zone in zones]

        response_data = ZoneListResponse(
            zones=zones_data,
            total=total,
            page=page,
            page_size=page_size,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error listing zones: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list zones",
        )


@router.get(
    "/{zone_id}",
    response_model=APIResponse,
    summary="Get zone details",
    description="Get detailed zone information with GeoJSON geometry",
)
async def get_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get detailed zone information.

    Args:
        zone_id: Zone UUID
        db: Database session

    Returns:
        APIResponse with zone data
    """
    logger.info(f"Fetching zone: id={zone_id}")

    try:
        zone = await ZoneService.get_zone(db=db, zone_id=zone_id)

        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone {zone_id} not found",
            )

        # Convert to response format with GeoJSON
        zone_dict = ZoneService._zone_to_dict(zone)
        response_data = ZoneResponse.model_validate(zone_dict)

        return success_response(data=response_data.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch zone",
        )


@router.put(
    "/{zone_id}",
    response_model=APIResponse,
    summary="Update zone",
    description="Update an existing zone",
)
async def update_zone(
    zone_id: UUID,
    zone_data: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Update an existing zone.

    Args:
        zone_id: Zone UUID
        zone_data: Zone update data (all fields optional)
        db: Database session

    Returns:
        APIResponse with updated zone
    """
    logger.info(f"Updating zone: id={zone_id}")

    try:
        zone = await ZoneService.update_zone(
            db=db,
            zone_id=zone_id,
            name=zone_data.name,
            description=zone_data.description,
            zone_type=zone_data.zone_type,
            risk_level=zone_data.risk_level,
            geometry=zone_data.geometry,
            field_id=zone_data.field_id,
            farm_id=zone_data.farm_id,
            extra_metadata=zone_data.extra_metadata,
        )

        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone {zone_id} not found",
            )

        # Convert to response format with GeoJSON
        zone_dict = ZoneService._zone_to_dict(zone)
        response_data = ZoneResponse.model_validate(zone_dict)

        return success_response(data=response_data.model_dump())

    except ValueError as e:
        logger.error(f"Validation error updating zone: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update zone",
        )


@router.delete(
    "/{zone_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete zone",
    description="Delete a zone",
)
async def delete_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a zone.

    Args:
        zone_id: Zone UUID
        db: Database session

    Returns:
        No content (204)
    """
    logger.info(f"Deleting zone: id={zone_id}")

    try:
        deleted = await ZoneService.delete_zone(db=db, zone_id=zone_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone {zone_id} not found",
            )

        # 204 No Content - no response body

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting zone: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete zone",
        )

