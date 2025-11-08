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
from app.schemas.explanation import ExplanationRequest, AgentExplanation
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.chat_history import (
    ChatHistoryResponse,
    ChatConversationListResponse,
    ChatMessageResponse,
    ChatConversationSummary,
)
from app.services.recommendation import RecommendationService
from app.services.explanation import ExplanationService
from app.services.chat import ChatService
from app.services.chat_history import ChatHistoryService

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


@router.post(
    "/irrigation/explain",
    response_model=APIResponse,
    summary="Explain irrigation recommendation",
    description="Get detailed explanation of how the agent made a recommendation decision",
)
async def explain_irrigation_recommendation(
    request: ExplanationRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Generate a detailed explanation for an irrigation recommendation.

    Provides transparency into:
    - Decision factors and their weights
    - Data sources used
    - Confidence breakdown
    - Alternative scenarios considered
    - Impact metrics

    Args:
        request: Explanation request with recommendation_id
        db: Database session

    Returns:
        APIResponse with detailed explanation
    """
    logger.info(f"Generating explanation for recommendation {request.recommendation_id}")

    try:
        explanation = await ExplanationService.explain_recommendation(
            db=db,
            recommendation_id=request.recommendation_id,
            include_alternatives=request.include_alternatives,
            include_data_sources=request.include_data_sources,
        )

        if not explanation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {request.recommendation_id} not found",
            )

        return success_response(
            data=explanation.model_dump(),
            message="Explanation generated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating explanation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation",
        )


@router.get(
    "/irrigation/recommendations/{recommendation_id}/explain",
    response_model=APIResponse,
    summary="Explain recommendation (GET)",
    description="Get detailed explanation of a recommendation (alternative GET endpoint)",
)
async def get_recommendation_explanation(
    recommendation_id: UUID,
    include_alternatives: bool = True,
    include_data_sources: bool = True,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get explanation for a recommendation (GET endpoint).

    Args:
        recommendation_id: ID of the recommendation
        include_alternatives: Whether to include alternative scenarios
        include_data_sources: Whether to include detailed data sources
        db: Database session

    Returns:
        APIResponse with detailed explanation
    """
    logger.info(f"Getting explanation for recommendation {recommendation_id}")

    try:
        explanation = await ExplanationService.explain_recommendation(
            db=db,
            recommendation_id=recommendation_id,
            include_alternatives=include_alternatives,
            include_data_sources=include_data_sources,
        )

        if not explanation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation {recommendation_id} not found",
            )

        return success_response(
            data=explanation.model_dump(),
            message="Explanation retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting explanation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get explanation",
        )


# Initialize chat service
chat_service = ChatService()


@router.post(
    "/chat",
    response_model=APIResponse,
    summary="Chat with AI agent",
    description="Send a natural language message to the AI agent and get a contextual response",
)
async def chat_with_agent(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Chat with the AI agent using natural language.

    The agent can answer questions about:
    - Field conditions and sensor data
    - Irrigation recommendations
    - Fire risk assessments
    - PSPS predictions
    - Water efficiency metrics
    - Alerts and notifications

    Args:
        request: Chat request with message and optional context
        db: Database session

    Returns:
        APIResponse with agent response
    """
    logger.info(f"Chat request: {request.message[:100]}...")

    try:
        response = await chat_service.process_message(
            db=db,
            message=request.message,
            conversation_id=request.conversation_id,
            field_id=request.field_id,
            include_context=request.include_context,
        )

        response_data = ChatResponse(**response)

        return success_response(
            data=response_data.model_dump(),
            message="Chat response generated successfully",
        )

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message",
        )


@router.get(
    "/chat/conversations",
    response_model=APIResponse,
    summary="List chat conversations",
    description="Get paginated list of chat conversations",
)
async def list_conversations(
    field_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List chat conversations with optional filtering.

    Args:
        field_id: Optional field ID filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        db: Database session

    Returns:
        APIResponse with paginated conversations
    """
    logger.info(
        f"Listing conversations: field_id={field_id}, page={page}, page_size={page_size}"
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
        conversations, total = await ChatHistoryService.list_conversations(
            db=db,
            field_id=field_id,
            page=page,
            page_size=page_size,
        )

        response_data = ChatConversationListResponse(
            conversations=[
                ChatConversationSummary(**conv) for conv in conversations
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list conversations",
        )


@router.get(
    "/chat/conversations/{conversation_id}",
    response_model=APIResponse,
    summary="Get conversation history",
    description="Get full conversation history for a conversation ID",
)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get conversation history.

    Args:
        conversation_id: Conversation ID
        limit: Optional limit on number of messages
        db: Database session

    Returns:
        APIResponse with conversation history
    """
    logger.info(f"Getting conversation history: conversation_id={conversation_id}")

    try:
        messages = await ChatHistoryService.get_conversation_history(
            db=db,
            conversation_id=conversation_id,
            limit=limit,
        )

        # Get field_id from first message if available
        field_id = messages[0].field_id if messages else None

        response_data = ChatHistoryResponse(
            conversation_id=conversation_id,
            messages=[ChatMessageResponse.model_validate(msg) for msg in messages],
            total=len(messages),
            field_id=field_id,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error getting conversation history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation history",
        )


@router.delete(
    "/chat/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete conversation",
    description="Delete a conversation and all its messages",
)
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a conversation.

    Args:
        conversation_id: Conversation ID
        db: Database session

    Returns:
        No content (204)
    """
    logger.info(f"Deleting conversation: conversation_id={conversation_id}")

    try:
        deleted = await ChatHistoryService.delete_conversation(
            db=db, conversation_id=conversation_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )

        # 204 No Content - no response body

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation",
        )

