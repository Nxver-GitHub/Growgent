"""
Service layer for recommendation operations.

Handles business logic for creating, retrieving, and managing recommendations.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents import fire_adaptive_irrigation_agent
from app.models.recommendation import (
    AgentType,
    Recommendation,
    RecommendationAction,
)

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for recommendation management."""

    @staticmethod
    async def create_recommendation(
        db: AsyncSession,
        field_id: UUID,
        agent_type: AgentType = AgentType.FIRE_ADAPTIVE_IRRIGATION,
    ) -> Recommendation:
        """
        Create a new recommendation using the Fire-Adaptive Irrigation Agent.

        Args:
            db: Database session
            field_id: Field UUID
            agent_type: Type of agent generating recommendation

        Returns:
            Created Recommendation instance
        """
        logger.info(f"Creating recommendation for field {field_id}")

        # Run agent to get recommendation
        agent_state = await fire_adaptive_irrigation_agent.recommend(
            field_id=field_id, db=db
        )

        if agent_state.error:
            raise ValueError(f"Agent error: {agent_state.error}")

        if not agent_state.recommended_action:
            raise ValueError("Agent did not generate a recommendation")

        # Create recommendation record
        recommendation = Recommendation(
            field_id=field_id,
            agent_type=agent_type,
            action=agent_state.recommended_action,
            title=f"{agent_state.recommended_action.value} Irrigation",
            reason=agent_state.reasoning or "No reasoning provided",
            recommended_timing=agent_state.recommended_timing,
            zones_affected=",".join(agent_state.zones_affected or []),
            confidence=agent_state.confidence or 0.5,
            fire_risk_reduction_percent=agent_state.fire_risk_reduction_percent,
            water_saved_liters=agent_state.water_saved_liters,
            psps_alert=agent_state.psps_alert,
            accepted=False,
        )

        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)

        logger.info(f"Recommendation created: {recommendation.id}")
        return recommendation

    @staticmethod
    async def get_recommendation(
        db: AsyncSession,
        recommendation_id: UUID,
        include_field: bool = False,
    ) -> Optional[Recommendation]:
        """
        Get a single recommendation by ID.

        Args:
            db: Database session
            recommendation_id: Recommendation ID
            include_field: Whether to load field relationship

        Returns:
            Recommendation instance or None if not found
        """
        logger.debug(f"Fetching recommendation: id={recommendation_id}")

        query = select(Recommendation).where(Recommendation.id == recommendation_id)

        if include_field:
            query = query.options(selectinload(Recommendation.field))

        result = await db.execute(query)
        recommendation = result.scalar_one_or_none()

        if recommendation:
            logger.debug(f"Recommendation found: id={recommendation_id}")
        else:
            logger.debug(f"Recommendation not found: id={recommendation_id}")

        return recommendation

    @staticmethod
    async def list_recommendations(
        db: AsyncSession,
        field_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
        action: Optional[RecommendationAction] = None,
        accepted: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        include_field: bool = False,
    ) -> tuple[list[Recommendation], int]:
        """
        List recommendations with filtering and pagination.

        Args:
            db: Database session
            field_id: Optional field ID filter
            agent_type: Optional agent type filter
            action: Optional action filter
            accepted: Optional accepted status filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_field: Whether to load field relationships

        Returns:
            Tuple of (recommendations list, total count)
        """
        logger.debug(
            f"Listing recommendations: field_id={field_id}, "
            f"agent_type={agent_type}, page={page}, page_size={page_size}"
        )

        # Build query
        query = select(Recommendation)

        if field_id:
            query = query.where(Recommendation.field_id == field_id)
        if agent_type:
            query = query.where(Recommendation.agent_type == agent_type)
        if action:
            query = query.where(Recommendation.action == action)
        if accepted is not None:
            query = query.where(Recommendation.accepted == accepted)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar_one() or 0

        # Apply pagination and ordering
        query = query.order_by(desc(Recommendation.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        if include_field:
            query = query.options(selectinload(Recommendation.field))

        result = await db.execute(query)
        recommendations = list(result.scalars().all())

        logger.debug(f"Found {len(recommendations)} recommendations (total: {total})")
        return recommendations, total

    @staticmethod
    async def accept_recommendation(
        db: AsyncSession,
        recommendation_id: UUID,
    ) -> Optional[Recommendation]:
        """
        Accept a recommendation.

        Args:
            db: Database session
            recommendation_id: Recommendation ID

        Returns:
            Updated Recommendation instance or None if not found
        """
        logger.info(f"Accepting recommendation: id={recommendation_id}")

        recommendation = await RecommendationService.get_recommendation(
            db, recommendation_id
        )

        if not recommendation:
            return None

        if recommendation.accepted:
            logger.warning(f"Recommendation {recommendation_id} already accepted")
            return recommendation

        recommendation.accepted = True
        recommendation.accepted_at = datetime.now()

        await db.commit()
        await db.refresh(recommendation)

        logger.info(f"Recommendation {recommendation_id} accepted")
        return recommendation

