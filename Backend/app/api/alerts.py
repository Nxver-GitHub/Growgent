"""
API routes for alert operations.

Handles endpoints for alert management and retrieval.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.models.alert import AlertSeverity, AlertType, AgentType
from app.schemas.alert import AlertCreate, AlertListResponse, AlertResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get(
    "",
    response_model=APIResponse,
    summary="List alerts",
    description="Get paginated list of alerts with optional filters",
)
async def list_alerts(
    field_id: Optional[UUID] = None,
    severity: Optional[AlertSeverity] = None,
    alert_type: Optional[AlertType] = None,
    agent_type: Optional[AgentType] = None,
    acknowledged: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    List alerts with optional filtering.

    Args:
        field_id: Optional field ID filter
        severity: Optional severity filter
        agent_type: Optional agent type filter
        acknowledged: Optional acknowledged status filter
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        db: Database session

    Returns:
        APIResponse with paginated alerts
    """
    logger.info(
        f"Listing alerts: field_id={field_id}, severity={severity}, "
        f"alert_type={alert_type}, agent_type={agent_type}, "
        f"acknowledged={acknowledged}, page={page}, page_size={page_size}"
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
        # Import here to avoid circular dependency
        from app.services.alert import AlertService

        alerts, total = await AlertService.list_alerts(
            db=db,
            field_id=field_id,
            severity=severity,
            alert_type=alert_type,
            agent_type=agent_type,
            acknowledged=acknowledged,
            page=page,
            page_size=page_size,
            include_field=True,
        )

        response_data = AlertListResponse(
            alerts=[AlertResponse.model_validate(alert) for alert in alerts],
            total=total,
            page=page,
            page_size=page_size,
        )

        return success_response(data=response_data.model_dump())

    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list alerts",
        )


@router.post(
    "/{alert_id}/acknowledge",
    response_model=APIResponse,
    summary="Acknowledge alert",
    description="Mark an alert as acknowledged",
)
async def acknowledge_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Acknowledge an alert.

    Args:
        alert_id: Alert UUID
        db: Database session

    Returns:
        APIResponse with updated alert
    """
    logger.info(f"Acknowledging alert: id={alert_id}")

    try:
        from app.services.alert import AlertService

        alert = await AlertService.acknowledge_alert(db=db, alert_id=alert_id)

        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Alert {alert_id} not found",
            )

        response_data = AlertResponse.model_validate(alert)

        return success_response(
            data=response_data.model_dump(),
            message="Alert acknowledged successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert",
        )


@router.post(
    "/create",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create alert (internal)",
    description="Create a new alert (typically called by agents)",
)
async def create_alert(
    alert_data: AlertCreate,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Create a new alert.

    This endpoint is typically called internally by agents to create alerts.
    For external use, alerts are created automatically by agents.

    Args:
        alert_data: Alert creation data
        db: Database session

    Returns:
        APIResponse with created alert
    """
    logger.info(
        f"Creating alert: type={alert_data.alert_type.value}, "
        f"severity={alert_data.severity.value}, field_id={alert_data.field_id}"
    )

    try:
        from app.services.alert import AlertService

        alert = await AlertService.create_alert(
            db=db,
            field_id=alert_data.field_id,
            alert_type=alert_data.alert_type,
            severity=alert_data.severity,
            message=alert_data.message,
            agent_type=alert_data.agent_type,
        )

        response_data = AlertResponse.model_validate(alert)

        return success_response(
            data=response_data.model_dump(),
            message="Alert created successfully",
        )

    except ValueError as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected error creating alert: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create alert",
        )


@router.get(
    "/critical",
    response_model=APIResponse,
    summary="Get critical alerts",
    description="Get critical alerts for dashboard priority display",
)
async def get_critical_alerts(
    field_id: Optional[UUID] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Get critical alerts (for dashboard priority display).

    Args:
        field_id: Optional field ID filter
        limit: Maximum number of alerts to return (default: 10, max: 50)
        db: Database session

    Returns:
        APIResponse with list of critical alerts
    """
    logger.info(f"Getting critical alerts: field_id={field_id}, limit={limit}")

    # Validate limit
    if limit < 1 or limit > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 50",
        )

    try:
        from app.services.alert import AlertService

        alerts = await AlertService.get_critical_alerts(
            db=db,
            field_id=field_id,
            limit=limit,
        )

        response_data = [AlertResponse.model_validate(alert).model_dump() for alert in alerts]

        return success_response(
            data={"alerts": response_data, "count": len(response_data)},
            message=f"Found {len(response_data)} critical alerts",
        )

    except Exception as e:
        logger.error(f"Error getting critical alerts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get critical alerts",
        )

