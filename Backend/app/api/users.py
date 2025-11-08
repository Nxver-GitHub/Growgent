"""
API routes for user profile operations.

Handles endpoints for user creation, updates, and profile management.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfileResponse
from app.services.user import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account with default preferences",
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Create a new user account.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        APIResponse with created user
    """
    try:
        # Check if user already exists
        existing = await UserService.get_user_by_email(db, user_data.email, include_preferences=False)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists",
            )

        user = await UserService.create_user(db, user_data)
        return success_response(
            data=UserResponse.model_validate(user),
            message="User created successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )


@router.get(
    "/{user_id}",
    response_model=APIResponse,
    summary="Get user",
    description="Get user profile by ID",
)
async def get_user(
    user_id: UUID,
    include_preferences: bool = True,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get user by ID.

    Args:
        user_id: User ID
        include_preferences: Whether to include preferences
        db: Database session

    Returns:
        APIResponse with user data
    """
    user = await UserService.get_user(db, user_id, include_preferences=include_preferences)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    # Build response with farms count
    response_data = UserProfileResponse.model_validate(user)
    response_data.farms_count = len(user.farms) if user.farms else 0
    response_data.has_preferences = user.preferences is not None

    return success_response(data=response_data)


@router.get(
    "/email/{email}",
    response_model=APIResponse,
    summary="Get user by email",
    description="Get user profile by email address",
)
async def get_user_by_email(
    email: str,
    include_preferences: bool = True,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get user by email.

    Args:
        email: User email
        include_preferences: Whether to include preferences
        db: Database session

    Returns:
        APIResponse with user data
    """
    user = await UserService.get_user_by_email(db, email, include_preferences=include_preferences)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found",
        )

    response_data = UserProfileResponse.model_validate(user)
    response_data.farms_count = len(user.farms) if user.farms else 0
    response_data.has_preferences = user.preferences is not None

    return success_response(data=response_data)


@router.put(
    "/{user_id}",
    response_model=APIResponse,
    summary="Update user",
    description="Update user profile information",
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Update user information.

    Args:
        user_id: User ID
        user_data: User update data
        db: Database session

    Returns:
        APIResponse with updated user
    """
    user = await UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return success_response(
        data=UserResponse.model_validate(user),
        message="User updated successfully",
    )


@router.get(
    "",
    response_model=APIResponse,
    summary="List users",
    description="Get paginated list of users",
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List users with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return (max 1000)
        is_active: Filter by active status
        db: Database session

    Returns:
        APIResponse with list of users
    """
    if limit > 1000:
        limit = 1000

    users = await UserService.list_users(db, skip=skip, limit=limit, is_active=is_active)
    return success_response(
        data=[UserResponse.model_validate(user) for user in users],
        message=f"Retrieved {len(users)} users",
    )

