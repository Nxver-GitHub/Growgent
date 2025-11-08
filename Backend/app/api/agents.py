"""
API routes for agent operations.

Handles endpoints for agent recommendations and agent-specific operations.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, error_response, success_response
from app.database import get_db
from app.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationListResponse,
)
from app.services.recommendation import RecommendationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.post(
    "/irrigation/recommend",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate irrigation recommendation",
    description="Generate a new irrigation recommendation using the Fire-Adaptive Irrigation Agent",
)
async def recommend_irrigation(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Generate irrigation recommendation for a field.

    Args:
        request: Recommendation request with field_id
        db: Database session

    Returns:
        APIResponse with recommendation data
    """
    logger.info(f"Generating irrigation recommendation for field {request.field_id}")

    try:
        recommendation = await RecommendationService.create_recommendation(
            db=db, field_id=request.field_id
        )

        response_data = RecommendationResponse.model_validate(recommendation)

        return success_response(
            data=response_data.model_dump(),
            message="Recommendation generated successfully",
        )

    except ValueError as e:
        logger.error(f"Error generating recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error generating recommendation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendation",
        )


@router.get(
    "/irrigation/recommendations",
    response_model=APIResponse,
    summary="List irrigation recommendations",
    description="Get paginated list of irrigation recommendations with optional filters",
)
async def list_irrigation_recommendations(
    field_id: Optional[UUID] = None,
    accepted: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List irrigation recommendations.

    Args:
        field_id: Optional field ID filter
        accepted: Optional accepted status filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        db: Database session

    Returns:
        APIResponse with paginated recommendations
    """
    logger.info(
        f"Listing irrigation recommendations: field_id={field_id}, "
        f"accepted={accepted}, page={page}, page_size={page_size}"
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
        from app.models.recommendation import AgentType

        recommendations, total = await RecommendationService.list_recommendations(
            db=db,
            field_id=field_id,
            agent_type=AgentType.FIRE_ADAPTIVE_IRRIGATION,
            accepted=accepted,
            page=page,
            page_size=page_size,
            include_field=True,
        )

        response_data = RecommendationListResponse(
            recommendations=[
                RecommendationResponse.model_validate(rec) for rec in recommendations
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error listing recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list recommendations",
        )

