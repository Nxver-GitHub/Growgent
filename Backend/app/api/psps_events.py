"""
API routes for PSPS (Public Safety Power Shutoff) event operations.

Handles endpoints for retrieving active and predicted PSPS events.
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.models.psps_event import PspsStatus
from app.schemas.psps_event import PspsEventResponse, PspsEventListResponse
from app.services.psps_event_service import get_active_psps_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/psps-events", tags=["psps-events"])


@router.get(
    "",
    response_model=APIResponse,
    summary="List active PSPS events",
    description="Retrieve a list of all active or predicted PSPS events from the database, optionally filtered by location and status.",
)
async def list_psps_events(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 0.1, # Default to a small radius for point intersection
    status_filter: Optional[PspsStatus] = None,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List all active or predicted PSPS events.

    Args:
        latitude: Optional latitude to filter events by proximity.
        longitude: Optional longitude to filter events by proximity.
        radius_km: Radius in kilometers for location-based filtering.
        status_filter: Optional filter by PSPS status (e.g., 'active', 'planned').
        db: Database session

    Returns:
        APIResponse with a list of PSPS events.
    """
    logger.info(f"Listing PSPS events: lat={latitude}, lon={longitude}, status={status_filter}")

    try:
        events = await get_active_psps_events(
            db=db,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            status_filter=status_filter,
        )
        
        # Convert models to schemas
        events_data = [PspsEventResponse.model_validate(e) for e in events]

        return success_response(data=events_data)

    except Exception as e:
        logger.error(f"Error listing PSPS events: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve PSPS events",
        )
