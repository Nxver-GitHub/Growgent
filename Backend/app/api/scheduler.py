"""
API routes for scheduler management.

Handles endpoints for viewing and managing agent scheduler jobs.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses import APIResponse, success_response
from app.database import get_db
from app.services.scheduler import scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get(
    "/status",
    response_model=APIResponse,
    summary="Get scheduler status",
    description="Get status of all scheduled agent jobs",
)
async def get_scheduler_status() -> APIResponse:
    """
    Get status of the agent scheduler and all scheduled jobs.

    Returns:
        APIResponse with scheduler status and job information
    """
    logger.info("Getting scheduler status")

    try:
        status_data = scheduler.get_job_status()

        return success_response(
            data=status_data,
            message="Scheduler status retrieved successfully",
        )

    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scheduler status",
        )


@router.post(
    "/jobs/{job_id}/trigger",
    response_model=APIResponse,
    summary="Trigger a scheduled job",
    description="Manually trigger a scheduled job to run immediately",
)
async def trigger_job(job_id: str) -> APIResponse:
    """
    Manually trigger a scheduled job.

    Args:
        job_id: ID of the job to trigger

    Returns:
        APIResponse with success status
    """
    logger.info(f"Triggering job: {job_id}")

    try:
        triggered = await scheduler.trigger_job(job_id)

        if not triggered:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found",
            )

        return success_response(
            data={"job_id": job_id, "triggered": True},
            message=f"Job {job_id} triggered successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering job: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger job",
        )

