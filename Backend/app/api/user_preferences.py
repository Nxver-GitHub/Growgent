"""
API routes for user preferences operations.

Handles endpoints for user preferences management that agents use for decision-making.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.user_preferences import (
    UserPreferencesCreate,
    UserPreferencesUpdate,
    UserPreferencesResponse,
)
from app.services.user import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users/{user_id}/preferences", tags=["user-preferences"])


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user preferences",
    description="Create preferences for a user (used by agents for decision-making)",
)
async def create_user_preferences(
    user_id: UUID,
    preferences_data: UserPreferencesCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Create user preferences.

    Args:
        user_id: User ID
        preferences_data: Preferences creation data
        db: Database session

    Returns:
        APIResponse with created preferences
    """
    # Verify user exists
    user = await UserService.get_user(db, user_id, include_preferences=False)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Check if preferences already exist
    existing = await UserService.get_user_preferences(db, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Preferences for user {user_id} already exist. Use PUT to update.",
        )

    from app.models.user_preferences import UserPreferences

    preferences = UserPreferences(
        user_id=user_id,
        **preferences_data.model_dump(exclude={"user_id"}),
    )
    db.add(preferences)
    await db.commit()
    await db.refresh(preferences)

    logger.info(f"Created preferences for user: {user_id}")

    return success_response(
        data=UserPreferencesResponse.model_validate(preferences),
        message="User preferences created successfully",
    )


@router.get(
    "",
    response_model=APIResponse,
    summary="Get user preferences",
    description="Get preferences for a user",
)
async def get_user_preferences(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get user preferences.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        APIResponse with user preferences
    """
    preferences = await UserService.get_user_preferences(db, user_id)
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preferences for user {user_id} not found",
        )

    return success_response(data=UserPreferencesResponse.model_validate(preferences))


@router.put(
    "",
    response_model=APIResponse,
    summary="Update user preferences",
    description="Update user preferences (all fields optional)",
)
async def update_user_preferences(
    user_id: UUID,
    preferences_data: UserPreferencesUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Update user preferences.

    Args:
        user_id: User ID
        preferences_data: Preferences update data
        db: Database session

    Returns:
        APIResponse with updated preferences
    """
    preferences = await UserService.get_user_preferences(db, user_id)
    if not preferences:
        # Create default preferences if they don't exist
        from app.models.user_preferences import UserPreferences

        preferences = UserPreferences(user_id=user_id)
        db.add(preferences)
        await db.flush()

    # Update fields
    update_data = preferences_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preferences, field, value)

    await db.commit()
    await db.refresh(preferences)

    logger.info(f"Updated preferences for user: {user_id}")

    return success_response(
        data=UserPreferencesResponse.model_validate(preferences),
        message="User preferences updated successfully",
    )

