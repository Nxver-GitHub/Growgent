"""
API routes for farm operations.

Handles endpoints for farm creation, updates, and management.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.farm import FarmCreate, FarmUpdate, FarmResponse
from app.services.farm import FarmService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/farms", tags=["farms"])


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create farm",
    description="Create a new farm for a user",
)
async def create_farm(
    farm_data: FarmCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Create a new farm.

    Args:
        farm_data: Farm creation data
        db: Database session

    Returns:
        APIResponse with created farm
    """
    try:
        # Check if farm_id already exists
        existing = await FarmService.get_farm_by_farm_id(db, farm_data.farm_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Farm with farm_id {farm_data.farm_id} already exists",
            )

        farm = await FarmService.create_farm(db, farm_data)

        # Get field count
        farm_with_count = await FarmService.get_farm_with_field_count(db, farm.id)
        fields_count = farm_with_count["fields_count"] if farm_with_count else 0

        response_data = FarmResponse.model_validate(farm)
        response_data.fields_count = fields_count
        if farm.location_geom:
            # Extract lat/lon from PostGIS geometry if needed
            # For now, set to None - can be extracted in response model
            response_data.latitude = None
            response_data.longitude = None

        return success_response(
            data=response_data,
            message="Farm created successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating farm: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create farm: {str(e)}",
        )


@router.get(
    "/{farm_id}",
    response_model=APIResponse,
    summary="Get farm",
    description="Get farm by UUID",
)
async def get_farm(
    farm_id: UUID,
    include_fields: bool = False,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get farm by ID.

    Args:
        farm_id: Farm UUID
        include_fields: Whether to include fields
        db: Database session

    Returns:
        APIResponse with farm data
    """
    farm = await FarmService.get_farm(db, farm_id, include_fields=include_fields)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id {farm_id} not found",
        )

    # Get field count
    farm_with_count = await FarmService.get_farm_with_field_count(db, farm_id)
    fields_count = farm_with_count["fields_count"] if farm_with_count else 0

    response_data = FarmResponse.model_validate(farm)
    response_data.fields_count = fields_count

    return success_response(data=response_data)


@router.get(
    "/farm-id/{farm_id_str}",
    response_model=APIResponse,
    summary="Get farm by farm_id",
    description="Get farm by legacy farm_id string",
)
async def get_farm_by_farm_id(
    farm_id_str: str,
    include_fields: bool = False,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get farm by farm_id string (legacy identifier).

    Args:
        farm_id_str: Farm ID string
        include_fields: Whether to include fields
        db: Database session

    Returns:
        APIResponse with farm data
    """
    farm = await FarmService.get_farm_by_farm_id(db, farm_id_str, include_fields=include_fields)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with farm_id {farm_id_str} not found",
        )

    farm_with_count = await FarmService.get_farm_with_field_count(db, farm.id)
    fields_count = farm_with_count["fields_count"] if farm_with_count else 0

    response_data = FarmResponse.model_validate(farm)
    response_data.fields_count = fields_count

    return success_response(data=response_data)


@router.put(
    "/{farm_id}",
    response_model=APIResponse,
    summary="Update farm",
    description="Update farm information",
)
async def update_farm(
    farm_id: UUID,
    farm_data: FarmUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Update farm information.

    Args:
        farm_id: Farm UUID
        farm_data: Farm update data
        db: Database session

    Returns:
        APIResponse with updated farm
    """
    farm = await FarmService.update_farm(db, farm_id, farm_data)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id {farm_id} not found",
        )

    farm_with_count = await FarmService.get_farm_with_field_count(db, farm_id)
    fields_count = farm_with_count["fields_count"] if farm_with_count else 0

    response_data = FarmResponse.model_validate(farm)
    response_data.fields_count = fields_count

    return success_response(
        data=response_data,
        message="Farm updated successfully",
    )


@router.get(
    "/owner/{owner_id}",
    response_model=APIResponse,
    summary="List farms by owner",
    description="Get all farms owned by a user",
)
async def list_farms_by_owner(
    owner_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List farms owned by a user.

    Args:
        owner_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return (max 1000)
        db: Database session

    Returns:
        APIResponse with list of farms
    """
    if limit > 1000:
        limit = 1000

    farms = await FarmService.list_farms_by_owner(db, owner_id, skip=skip, limit=limit)

    # Get field counts for each farm
    farms_data = []
    for farm in farms:
        farm_with_count = await FarmService.get_farm_with_field_count(db, farm.id)
        fields_count = farm_with_count["fields_count"] if farm_with_count else 0

        response_data = FarmResponse.model_validate(farm)
        response_data.fields_count = fields_count
        farms_data.append(response_data)

    return success_response(
        data=farms_data,
        message=f"Retrieved {len(farms_data)} farms",
    )

