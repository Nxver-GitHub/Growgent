"""
Agent scheduler service for running agents automatically.

Uses APScheduler to run agents on a schedule, making the platform
truly autonomous without manual intervention.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.agents.irrigation import FireAdaptiveIrrigationAgent, IrrigationAgentState
from app.agents.psps import PSPSAlertAgent, PSPSAgentState
from app.agents.water_efficiency import WaterEfficiencyAgent, WaterEfficiencyAgentState
from app.models.field import Field
from app.services.field import FieldService
from app.services.alert import AlertService
from app.services.psps_event_service import sync_psps_events # Added
from app.services.fire_perimeter_service import sync_fire_perimeters # Added

logger = logging.getLogger(__name__)


class AgentScheduler:
    """
    Scheduler for running agents automatically.

    Manages scheduled jobs for:
    - Irrigation agent (checks all fields periodically)
    - PSPS agent (monitors shutoffs every 30 minutes)
    - Water efficiency agent (calculates metrics periodically)
    - PSPS event synchronization (fetches latest PSPS data)
    - Fire perimeter synchronization (fetches latest fire data)
    """

    def __init__(self) -> None:
        """Initialize the agent scheduler."""
        self.scheduler = AsyncIOScheduler()
        self.irrigation_agent = FireAdaptiveIrrigationAgent()
        self.psps_agent = PSPSAlertAgent()
        self.water_efficiency_agent = WaterEfficiencyAgent()
        self._is_running = False

    async def start(self) -> None:
        """Start the scheduler and register all jobs."""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting agent scheduler...")

        # Schedule Irrigation Agent - Check all fields every 6 hours
        self.scheduler.add_job(
            self._run_irrigation_agent_all_fields,
            trigger=IntervalTrigger(hours=6),
            id="irrigation_agent_all_fields",
            name="Fire-Adaptive Irrigation Agent (All Fields)",
            replace_existing=True,
        )

        # Schedule PSPS Agent - Check for shutoffs every 30 minutes
        self.scheduler.add_job(
            self._run_psps_agent,
            trigger=IntervalTrigger(minutes=30),
            id="psps_agent_monitor",
            name="PSPS Alert Agent",
            replace_existing=True,
        )

        # Schedule Water Efficiency Agent - Calculate metrics every 4 hours
        self.scheduler.add_job(
            self._run_water_efficiency_agent_all_fields,
            trigger=IntervalTrigger(hours=4),
            id="water_efficiency_agent_all_fields",
            name="Water Efficiency Agent (All Fields)",
            replace_existing=True,
        )

        # Schedule PSPS event synchronization - Every 5 minutes (as per DATA_PLAN.md)
        self.scheduler.add_job(
            self._run_psps_sync_job,
            trigger=IntervalTrigger(minutes=5),
            id="psps_sync_job",
            name="PSPS Event Synchronization",
            replace_existing=True,
        )

        # Schedule Fire perimeter synchronization - Every 10 minutes (as per DATA_PLAN.md)
        self.scheduler.add_job(
            self._run_fire_perimeter_sync_job,
            trigger=IntervalTrigger(minutes=10),
            id="fire_perimeter_sync_job",
            name="Fire Perimeter Synchronization",
            replace_existing=True,
        )

        self.scheduler.start()
        self._is_running = True
        logger.info("Agent scheduler started successfully")
        logger.info("  - Irrigation Agent: Every 6 hours")
        logger.info("  - PSPS Agent: Every 30 minutes")
        logger.info("  - Water Efficiency Agent: Every 4 hours")
        logger.info("  - PSPS Event Sync: Every 5 minutes")
        logger.info("  - Fire Perimeter Sync: Every 10 minutes")

    async def stop(self) -> None:
        """Stop the scheduler."""
        if not self._is_running:
            return

        logger.info("Stopping agent scheduler...")
        self.scheduler.shutdown(wait=True)
        self._is_running = False
        logger.info("Agent scheduler stopped")

    async def _run_irrigation_agent_all_fields(self) -> None:
        """
        Run irrigation agent for all fields.

        This job runs periodically to check all fields and generate
        recommendations automatically.
        """
        logger.info("Running irrigation agent for all fields...")

        # Get database session
        async for db in get_db():
            try:
                # Get all fields
                fields, total = await FieldService.list_fields(
                    db=db, page=1, page_size=1000  # Get all fields
                )

                logger.info(f"Processing {len(fields)} fields with irrigation agent")

                recommendations_created = 0
                errors = 0

                for field in fields:
                    try:
                        # Run irrigation agent for this field
                        state = IrrigationAgentState(field_id=field.id)
                        state = await self.irrigation_agent.process(state, db=db)

                        if state.error:
                            logger.error(
                                f"Error processing field {field.id}: {state.error}"
                            )
                            errors += 1
                        elif state.recommended_action:
                            recommendations_created += 1
                            logger.debug(
                                f"Field {field.id}: {state.recommended_action.value}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Exception processing field {field.id}: {e}", exc_info=True
                        )
                        errors += 1

                logger.info(
                    f"Irrigation agent complete: {recommendations_created} recommendations, "
                    f"{errors} errors"
                )

            except Exception as e:
                logger.error(f"Error in irrigation agent job: {e}", exc_info=True)
            finally:
                break  # Exit the async generator

    async def _run_psps_agent(self) -> None:
        """
        Run PSPS agent to monitor for power shutoffs.

        This job runs every 30 minutes to check for new PSPS events
        and generate alerts.
        """
        logger.info("Running PSPS agent to monitor shutoffs...")

        # Get database session
        async for db in get_db():
            try:
                # Run PSPS agent (it handles finding affected fields internally)
                state = PSPSAgentState()
                state = await self.psps_agent.process(state, db=db)

                if state.error:
                    logger.error(f"PSPS agent error: {state.error}")
                else:
                    logger.info(
                        f"PSPS agent complete: {state.alerts_created} alerts created, "
                        f"{len(state.affected_field_ids)} fields affected"
                    )

            except Exception as e:
                logger.error(f"Error in PSPS agent job: {e}", exc_info=True)
            finally:
                break  # Exit the async generator

    async def _run_water_efficiency_agent_all_fields(self) -> None:
        """
        Run water efficiency agent for all fields.

        This job runs periodically to calculate water efficiency metrics
        for all fields.
        """
        logger.info("Running water efficiency agent for all fields...")

        # Get database session
        async for db in get_db():
            try:
                # Get all fields
                fields, total = await FieldService.list_fields(
                    db=db, page=1, page_size=1000  # Get all fields
                )

                logger.info(f"Processing {len(fields)} fields with water efficiency agent")

                metrics_updated = 0
                errors = 0

                for field in fields:
                    try:
                        state = WaterEfficiencyAgentState(field_id=field.id)
                        state = await self.water_efficiency_agent.process(state, db=db)

                        if state.error:
                            logger.error(
                                f"Error processing field {field.id}: {state.error}"
                            )
                            errors += 1
                        else:
                            metrics_updated += 1
                            logger.debug(f"Field {field.id}: Metrics updated")

                    except Exception as e:
                        logger.error(
                            f"Exception processing field {field.id}: {e}", exc_info=True
                        )
                        errors += 1

                logger.info(
                    f"Water efficiency agent complete: {metrics_updated} fields updated, "
                    f"{errors} errors"
                )

            except Exception as e:
                logger.error(f"Error in water efficiency agent job: {e}", exc_info=True)
            finally:
                break  # Exit the async generator

    def get_job_status(self) -> Dict[str, Any]:
        """
        Get status of all scheduled jobs.

        Returns:
            Dict with job status information
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })

        return {
            "running": self._is_running,
            "jobs": jobs,
            "total_jobs": len(jobs),
        }

    async def trigger_job(self, job_id: str) -> bool:
        """
        Manually trigger a scheduled job.

        Args:
            job_id: ID of the job to trigger

        Returns:
            True if job was triggered, False if not found
        """
        job = self.scheduler.get_job(job_id)
        if not job:
            return False

        logger.info(f"Manually triggering job: {job_id}")
        job.modify(next_run_time=datetime.now())
        return True


    async def _run_psps_sync_job(self) -> None:
        """
        Run PSPS event synchronization job.
        """
        logger.info("Running PSPS event synchronization job...")
        async for db in get_db():
            try:
                await sync_psps_events(db)
            except Exception as e:
                logger.error(f"Error in PSPS event sync job: {e}", exc_info=True)
            finally:
                break

    async def _run_fire_perimeter_sync_job(self) -> None:
        """
        Run Fire perimeter synchronization job.
        """
        logger.info("Running Fire perimeter synchronization job...")
        async for db in get_db():
            try:
                await sync_fire_perimeters(db)
            except Exception as e:
                logger.error(f"Error in Fire perimeter sync job: {e}", exc_info=True)
            finally:
                break


# Global scheduler instance
scheduler = AgentScheduler()

