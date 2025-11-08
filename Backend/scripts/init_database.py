#!/usr/bin/env python3
"""
Database initialization script.

This script initializes the PostgreSQL database with all tables and extensions.
Run this after starting the PostgreSQL container.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import init_db, close_db
from app.config import settings

# Import all models to ensure they're registered with Base.metadata
from app.models import Field, SensorReading, Recommendation, Alert, Zone, ChatMessage  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Initialize the database."""
    logger.info("Starting database initialization...")
    logger.info(f"Database URL: {settings.database_url.replace('postgresql://', 'postgresql://***@', 1)}")

    try:
        await init_db()
        logger.info("✅ Database initialized successfully!")
        logger.info("   - PostGIS extension enabled")
        logger.info("   - All tables created")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        logger.error("   Make sure PostgreSQL is running and accessible")
        sys.exit(1)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())

