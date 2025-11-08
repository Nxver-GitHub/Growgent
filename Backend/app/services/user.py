"""
User service for user profile management.

Handles user creation, updates, and profile management operations.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserRole
from app.models.user_preferences import UserPreferences
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user profile management."""

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        """
        Create a new user with default preferences.

        Args:
            db: Database session
            user_data: User creation data

        Returns:
            Created user
        """
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            phone=user_data.phone,
            role=user_data.role,
        )
        db.add(user)
        await db.flush()  # Flush to get user.id

        # Create default preferences
        preferences = UserPreferences(
            user_id=user.id,
            email_notifications_enabled=True,
            push_notifications_enabled=True,
            psps_alerts_enabled=True,
            water_milestone_alerts_enabled=True,
            fire_risk_alerts_enabled=True,
        )
        db.add(preferences)

        await db.commit()
        await db.refresh(user)
        await db.refresh(preferences)

        logger.info(f"Created user: {user.email} (id: {user.id})")
        return user

    @staticmethod
    async def get_user(
        db: AsyncSession,
        user_id: UUID,
        include_preferences: bool = True,
    ) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID
            include_preferences: Whether to include preferences

        Returns:
            User if found, None otherwise
        """
        query = select(User).where(User.id == user_id)

        if include_preferences:
            query = query.options(selectinload(User.preferences))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
        include_preferences: bool = True,
    ) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: User email
            include_preferences: Whether to include preferences

        Returns:
            User if found, None otherwise
        """
        query = select(User).where(User.email == email)

        if include_preferences:
            query = query.options(selectinload(User.preferences))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        user_data: UserUpdate,
    ) -> Optional[User]:
        """
        Update user information.

        Args:
            db: Database session
            user_id: User ID
            user_data: User update data

        Returns:
            Updated user if found, None otherwise
        """
        user = await UserService.get_user(db, user_id, include_preferences=False)
        if not user:
            return None

        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await db.commit()
        await db.refresh(user)

        logger.info(f"Updated user: {user.email} (id: {user.id})")
        return user

    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> list[User]:
        """
        List users with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status

        Returns:
            List of users
        """
        query = select(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_user_preferences(
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[UserPreferences]:
        """
        Get user preferences.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User preferences if found, None otherwise
        """
        result = await db.execute(
            select(UserPreferences).where(UserPreferences.user_id == user_id)
        )
        return result.scalar_one_or_none()

