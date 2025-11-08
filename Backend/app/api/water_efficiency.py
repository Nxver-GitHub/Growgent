"""
API routes for water efficiency agent operations.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, error_response, success_response
from app.database import get_db
from app.agents.water_efficiency import water_efficiency_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents/water-efficiency", tags=["agents"])


@router.post(
    "/analyze",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze water efficiency for a field",
)
async def analyze_water_efficiency(
    field_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Analyze water efficiency for a given field over a time period.
    """
    logger.info(f"Analyzing water efficiency for field {field_id}")

    try:
        # In a real implementation, you would pass a time period from the request
        agent_state = await water_efficiency_agent.analyze(db=db, field_id=field_id)

        if agent_state.error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=agent_state.error,
            )

        return success_response(
            data=agent_state.model_dump(),
            message="Water efficiency analysis complete",
        )

    except Exception as e:
        logger.error(f"Unexpected error analyzing water efficiency: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze water efficiency",
        )
