"""
API routes for utility shutoff agent operations.
"""

import logging
from uuid import UUID
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, error_response, success_response
from app.database import get_db
from app.agents.utility_shutoff import utility_shutoff_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents/utility-shutoff", tags=["agents"])


class UtilityShutoffCheckRequest(BaseModel):
    field_id: UUID
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


@router.post(
    "/check",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Check for utility shutoffs for a location",
)
async def check_for_shutoffs(
    request: UtilityShutoffCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Check for potential utility shutoffs for a given location.
    """
    logger.info(f"Checking for utility shutoffs for field {request.field_id}")

    try:
        location = {"latitude": request.latitude, "longitude": request.longitude}
        agent_state = await utility_shutoff_agent.check_for_shutoffs(
            field_id=request.field_id, location=location
        )

        if agent_state.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=agent_state.error,
            )

        return success_response(
            data=agent_state.model_dump(),
            message="Utility shutoff check complete",
        )

    except Exception as e:
        logger.error(f"Unexpected error checking for shutoffs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check for utility shutoffs",
        )
