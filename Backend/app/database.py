"""
Database connection and session management.

This module sets up SQLAlchemy async engine, session factory, and database
initialization for PostgreSQL with PostGIS support.
"""
import os
from dotenv import load_dotenv


import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings
print("🧱 settings.database_url =", settings.database_url)


# Load environment variables from .env in project root
load_dotenv()

print("🔧 Loaded DATABASE_URL:", os.getenv("DATABASE_URL"))
logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = settings.database_url.replace(
    "postgresql://", "postgresql+asyncpg://", 1
)

# Create async engine
# NullPool for development; use connection pooling in production
engine = create_async_engine(
    database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    poolclass=NullPool if settings.environment == "development" else None,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function for FastAPI to get database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database: create tables and enable PostGIS extension.

    This should be called once at application startup.
    """
    from sqlalchemy import text

    async with engine.begin() as conn:
        # Enable PostGIS extension for spatial queries
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            logger.info("PostGIS extension enabled")
        except Exception as e:
            logger.warning(f"Could not enable PostGIS extension: {e}")
            logger.warning("Spatial queries may not work. Ensure PostGIS is installed.")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


async def close_db() -> None:
    """
    Close database connections.

    This should be called at application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")

