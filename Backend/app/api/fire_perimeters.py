"""
API routes for fire perimeter operations.

Handles endpoints for retrieving active fire perimeters.
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.fire_perimeter import FirePerimeter
from app.services.fire_perimeter_service import get_active_fire_perimeters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/fire-perimeters", tags=["fire-perimeters"])


@router.get(
    "",
    response_model=APIResponse,
    summary="List active fire perimeters",
    description="Retrieve a list of all active fire perimeters from the database.",
)
async def list_fire_perimeters(
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List all active fire perimeters.

    Args:
        db: Database session

    Returns:
        APIResponse with a list of active fire perimeters.
    """
    logger.info("Listing active fire perimeters.")

    try:
        perimeters = await get_active_fire_perimeters(db)
        
        # Convert models to schemas
        perimeters_data = [FirePerimeter.model_validate(p) for p in perimeters]

        return success_response(data=perimeters_data)

    except Exception as e:
        logger.error(f"Error listing fire perimeters: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve fire perimeters",
        )
