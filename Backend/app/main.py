"""
FastAPI main application entry point.

This module initializes the FastAPI application with proper middleware,
CORS configuration, and route handlers for the Growgent API.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import agents, alerts, fields, recommendations, metrics, zones, scheduler as scheduler_api, satellite, users, farms, user_preferences
from app.config import settings
from app.database import init_db, close_db
from app.services.scheduler import scheduler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup: Initialize database
    logger.info("Starting Growgent API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Startup: Start agent scheduler
    try:
        await scheduler.start()
        logger.info("Agent scheduler started successfully")
    except Exception as e:
        logger.error(f"Failed to start agent scheduler: {e}")
        # Don't fail startup if scheduler fails, but log the error

    yield

    # Shutdown: Stop agent scheduler
    logger.info("Shutting down Growgent API...")
    try:
        await scheduler.stop()
        logger.info("Agent scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")

    # Shutdown: Close database connections
    await close_db()
    logger.info("Database connections closed")


app = FastAPI(
    title="Growgent API",
    description="Open-source agentic platform for climate-adaptive irrigation and wildfire management",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware - restrict origins in production
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",  # Vite default port (if used)
    # Add production frontend URL when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Register API routers
app.include_router(agents.router)
app.include_router(fields.router)
app.include_router(recommendations.router)
app.include_router(alerts.router)
app.include_router(metrics.router)
app.include_router(zones.router)
app.include_router(scheduler_api.router)
app.include_router(satellite.router)
app.include_router(users.router)
app.include_router(farms.router)
app.include_router(user_preferences.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: The FastAPI request object
        exc: The exception that was raised

    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not settings.debug else str(exc),
        },
    )


@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API information.

    Returns:
        Dictionary containing API name and version
    """
    return {"message": "Growgent API", "version": "0.1.0"}


@app.get("/health", tags=["health"])
async def health() -> Dict[str, str]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dictionary with health status
    """
    return {"status": "healthy"}
