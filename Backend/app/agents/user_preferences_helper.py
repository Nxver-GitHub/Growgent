"""
Helper functions for fetching user preferences from fields.

Provides utilities for agents to access user preferences based on field ownership.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.field import Field
from app.models.farm import Farm
from app.models.user_preferences import UserPreferences

logger = logging.getLogger(__name__)


async def get_user_preferences_for_field(
    db: AsyncSession,
    field_id: UUID,
) -> Optional[UserPreferences]:
    """
    Get user preferences for a field by traversing Field -> Farm -> User -> Preferences.

    Args:
        db: Database session
        field_id: Field ID

    Returns:
        UserPreferences if found, None otherwise
    """
    try:
        # Get field with farm relationship
        field_query = (
            select(Field)
            .where(Field.id == field_id)
            .options(selectinload(Field.farm).selectinload(Farm.owner).selectinload("preferences"))
        )
        result = await db.execute(field_query)
        field = result.scalar_one_or_none()

        if not field:
            logger.warning(f"Field {field_id} not found")
            return None

        # Try to get preferences via farm relationship
        if field.farm and field.farm.owner and field.farm.owner.preferences:
            return field.farm.owner.preferences

        # Fallback: Try to get farm by farm_id string and then user
        if field.farm_id:
            farm_query = (
                select(Farm)
                .where(Farm.farm_id == field.farm_id)
                .options(selectinload(Farm.owner).selectinload("preferences"))
            )
            farm_result = await db.execute(farm_query)
            farm = farm_result.scalar_one_or_none()

            if farm and farm.owner and farm.owner.preferences:
                return farm.owner.preferences

        logger.debug(f"No preferences found for field {field_id}")
        return None

    except Exception as e:
        logger.error(f"Error fetching user preferences for field {field_id}: {e}", exc_info=True)
        return None


async def get_user_preferences_for_farm(
    db: AsyncSession,
    farm_id: UUID,
) -> Optional[UserPreferences]:
    """
    Get user preferences for a farm.

    Args:
        db: Database session
        farm_id: Farm UUID

    Returns:
        UserPreferences if found, None otherwise
    """
    try:
        farm_query = (
            select(Farm)
            .where(Farm.id == farm_id)
            .options(selectinload(Farm.owner).selectinload("preferences"))
        )
        result = await db.execute(farm_query)
        farm = result.scalar_one_or_none()

        if not farm:
            return None

        if farm.owner and farm.owner.preferences:
            return farm.owner.preferences

        return None

    except Exception as e:
        logger.error(f"Error fetching user preferences for farm {farm_id}: {e}", exc_info=True)
        return None

