"""
Service layer for field operations.

Handles business logic for retrieving and managing fields.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.field import Field
from app.models.sensor_reading import SensorReading

logger = logging.getLogger(__name__)


class FieldService:
    """Service for field management."""

    @staticmethod
    async def get_field(
        db: AsyncSession,
        field_id: UUID,
        include_relations: bool = False,
    ) -> Optional[Field]:
        """
        Get a single field by ID.

        Args:
            db: Database session
            field_id: Field ID
            include_relations: Whether to load related data (sensor readings, etc.)

        Returns:
            Field instance or None if not found
        """
        logger.debug(f"Fetching field: id={field_id}")

        query = select(Field).where(Field.id == field_id)

        if include_relations:
            query = query.options(
                selectinload(Field.sensor_readings),
                selectinload(Field.recommendations),
                selectinload(Field.alerts),
            )

        result = await db.execute(query)
        field = result.scalar_one_or_none()

        if field:
            logger.debug(f"Field found: id={field_id}, name={field.name}")
        else:
            logger.debug(f"Field not found: id={field_id}")

        return field

    @staticmethod
    async def list_fields(
        db: AsyncSession,
        farm_id: Optional[str] = None,
        crop_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        include_latest_sensor: bool = True,
    ) -> tuple[list[Field], int]:
        """
        List fields with optional filtering and pagination.

        Args:
            db: Database session
            farm_id: Optional farm ID filter
            crop_type: Optional crop type filter
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_latest_sensor: Whether to include latest sensor reading

        Returns:
            Tuple of (fields list, total count)
        """
        logger.debug(
            f"Listing fields: farm_id={farm_id}, crop_type={crop_type}, "
            f"page={page}, page_size={page_size}"
        )

        # Build base query for filtering
        base_query = select(Field)

        if farm_id:
            base_query = base_query.where(Field.farm_id == farm_id)
        if crop_type:
            base_query = base_query.where(Field.crop_type == crop_type)

        # Get total count
        from sqlalchemy import func
        count_query = select(func.count(Field.id))
        if farm_id:
            count_query = count_query.where(Field.farm_id == farm_id)
        if crop_type:
            count_query = count_query.where(Field.crop_type == crop_type)
        count_result = await db.execute(count_query)
        total = count_result.scalar_one() or 0

        # Build paginated query
        query = base_query

        # Apply pagination and ordering
        query = query.order_by(desc(Field.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)

        if include_latest_sensor:
            query = query.options(selectinload(Field.sensor_readings))

        result = await db.execute(query)
        fields = list(result.scalars().all())

        # Get latest sensor reading for each field
        if include_latest_sensor:
            for field in fields:
                if field.sensor_readings:
                    # Sort by reading_timestamp and get latest
                    latest = max(
                        field.sensor_readings,
                        key=lambda r: r.reading_timestamp,
                        default=None,
                    )
                    # Store in metadata for easy access
                    field._latest_sensor_reading = latest

        logger.debug(f"Found {len(fields)} fields (total: {total})")
        return fields, total

    @staticmethod
    async def get_latest_sensor_reading(
        db: AsyncSession,
        field_id: UUID,
    ) -> Optional[SensorReading]:
        """
        Get the latest sensor reading for a field.

        Args:
            db: Database session
            field_id: Field ID

        Returns:
            Latest SensorReading or None if not found
        """
        logger.debug(f"Fetching latest sensor reading for field {field_id}")

        query = (
            select(SensorReading)
            .where(SensorReading.field_id == field_id)
            .order_by(desc(SensorReading.reading_timestamp))
            .limit(1)
        )

        result = await db.execute(query)
        reading = result.scalar_one_or_none()

        if reading:
            logger.debug(f"Latest sensor reading found for field {field_id}")
        else:
            logger.debug(f"No sensor readings found for field {field_id}")

        return reading

