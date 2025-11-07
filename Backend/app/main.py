"""
FastAPI main application entry point.

This module initializes the FastAPI application with proper middleware,
CORS configuration, and route handlers for the Growgent API.
"""

import logging
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Growgent API",
    description="Open-source agentic platform for climate-adaptive irrigation and wildfire management",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - restrict origins in production
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
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
