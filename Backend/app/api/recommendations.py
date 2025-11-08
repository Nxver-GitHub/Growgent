"""
API routes for recommendation operations.

Handles endpoints for recommendation management (accept, etc.).
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.post(
    "/{recommendation_id}/accept",
    response_model=APIResponse,
    summary="Accept recommendation",
    description="Accept a recommendation (trigger irrigation)",
)
async def accept_recommendation(
    recommendation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Accept a recommendation.

    Args:
        recommendation_id: Recommendation UUID
        db: Database session

    Returns:
        APIResponse with updated recommendation
    """
    logger.info(f"Accepting recommendation: id={recommendation_id}")

    try:
        recommendation = await RecommendationService.accept_recommendation(
            db=db, recommendation_id=recommendation_id
        )

        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found",
            )

        response_data = RecommendationResponse.model_validate(recommendation)

        return success_response(
            data=response_data.model_dump(),
            message="Recommendation accepted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error accepting recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept recommendation",
        )

