"""
Alert service for creating and managing alerts.

This service handles alert creation, retrieval, and acknowledgment.
All alerts are immutable (no editing, only create/acknowledge).
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.alert import Alert, AlertType, AlertSeverity, AgentType
from app.schemas.alert import AlertCreate

logger = logging.getLogger(__name__)


class AlertService:
    """Service for alert orchestration and management."""

    @staticmethod
    async def create_alert(
        db: AsyncSession,
        field_id: Optional[UUID],
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        agent_type: AgentType,
    ) -> Alert:
        """
        Create a new alert.

        Args:
            db: Database session
            field_id: Optional field ID (nullable for system-wide alerts)
            alert_type: Category/type of alert
            severity: Alert severity level
            message: Alert message text
            agent_type: Type of agent generating the alert

        Returns:
            Created Alert instance

        Raises:
            ValueError: If message is empty
        """
        logger.info(
            f"Creating alert: type={alert_type.value}, severity={severity.value}, "
            f"agent={agent_type.value}, field_id={field_id}"
        )

        if not message or not message.strip():
            raise ValueError("Alert message cannot be empty")

        alert = Alert(
            field_id=field_id,
            alert_type=alert_type,
            severity=severity,
            message=message.strip(),
            agent_type=agent_type,
            acknowledged=False,
            acknowledged_at=None,
        )

        db.add(alert)
        await db.flush()  # Flush to get the ID without committing
        await db.refresh(alert)

        logger.info(f"Alert created successfully: id={alert.id}")
        return alert

    @staticmethod
    async def get_alert(
        db: AsyncSession,
        alert_id: UUID,
        include_field: bool = False,
    ) -> Optional[Alert]:
        """
        Get a single alert by ID.

        Args:
            db: Database session
            alert_id: Alert ID
            include_field: Whether to load field relationship

        Returns:
            Alert instance or None if not found
        """
        logger.debug(f"Fetching alert: id={alert_id}")

        query = select(Alert).where(Alert.id == alert_id)

        if include_field:
            query = query.options(selectinload(Alert.field))

        result = await db.execute(query)
        alert = result.scalar_one_or_none()

        if alert:
            logger.debug(f"Alert found: id={alert_id}")
        else:
            logger.debug(f"Alert not found: id={alert_id}")

        return alert

    @staticmethod
    async def list_alerts(
        db: AsyncSession,
        field_id: Optional[UUID] = None,
        severity: Optional[AlertSeverity] = None,
        alert_type: Optional[AlertType] = None,
        agent_type: Optional[AgentType] = None,
        acknowledged: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
        include_field: bool = False,
    ) -> tuple[list[Alert], int]:
        """
        List alerts with filtering and pagination.

        Args:
            db: Database session
            field_id: Filter by field ID (optional)
            severity: Filter by severity (optional)
            alert_type: Filter by alert type (optional)
            agent_type: Filter by agent type (optional)
            acknowledged: Filter by acknowledgment status (optional)
            page: Page number (1-indexed)
            page_size: Number of items per page
            include_field: Whether to load field relationship

        Returns:
            Tuple of (list of alerts, total count)
        """
        logger.debug(
            f"Listing alerts: field_id={field_id}, severity={severity}, "
            f"alert_type={alert_type}, page={page}, page_size={page_size}"
        )

        # Build query with filters
        conditions = []

        if field_id:
            conditions.append(Alert.field_id == field_id)
        if severity:
            conditions.append(Alert.severity == severity)
        if alert_type:
            conditions.append(Alert.alert_type == alert_type)
        if agent_type:
            conditions.append(Alert.agent_type == agent_type)
        if acknowledged is not None:
            conditions.append(Alert.acknowledged == acknowledged)

        query = select(Alert)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = select(func.count()).select_from(Alert)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Alert.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        if include_field:
            query = query.options(selectinload(Alert.field))

        result = await db.execute(query)
        alerts = list(result.scalars().all())

        logger.debug(f"Found {len(alerts)} alerts (total: {total})")
        return alerts, total

    @staticmethod
    async def acknowledge_alert(
        db: AsyncSession,
        alert_id: UUID,
    ) -> Optional[Alert]:
        """
        Acknowledge an alert (mark as read).

        Args:
            db: Database session
            alert_id: Alert ID to acknowledge

        Returns:
            Updated Alert instance or None if not found
        """
        logger.info(f"Acknowledging alert: id={alert_id}")

        alert = await AlertService.get_alert(db, alert_id)

        if not alert:
            logger.warning(f"Alert not found for acknowledgment: id={alert_id}")
            return None

        if alert.acknowledged:
            logger.debug(f"Alert already acknowledged: id={alert_id}")
            return alert

        alert.acknowledged = True
        alert.acknowledged_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(alert)

        logger.info(f"Alert acknowledged successfully: id={alert_id}")
        return alert

    @staticmethod
    async def get_critical_alerts(
        db: AsyncSession,
        field_id: Optional[UUID] = None,
        limit: int = 10,
    ) -> list[Alert]:
        """
        Get critical alerts (for dashboard priority display).

        Args:
            db: Database session
            field_id: Filter by field ID (optional)
            limit: Maximum number of alerts to return

        Returns:
            List of critical alerts, ordered by creation date (newest first)
        """
        logger.debug(f"Fetching critical alerts: field_id={field_id}, limit={limit}")

        conditions = [Alert.severity == AlertSeverity.CRITICAL]

        if field_id:
            conditions.append(Alert.field_id == field_id)

        query = (
            select(Alert)
            .where(and_(*conditions))
            .where(Alert.acknowledged == False)  # Only unacknowledged
            .order_by(Alert.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(query)
        alerts = list(result.scalars().all())

        logger.debug(f"Found {len(alerts)} critical alerts")
        return alerts

