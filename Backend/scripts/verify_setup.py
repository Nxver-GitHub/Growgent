#!/usr/bin/env python3
"""
Verify database setup script.

Checks if PostgreSQL is running and accessible, and verifies database setup.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine, close_db
from app.config import settings

# Import all models to ensure they're registered
from app.models import Field, SensorReading, Recommendation, Alert, Zone, ChatMessage  # noqa: F401

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def verify_database() -> bool:
    """Verify database connection and setup."""
    logger.info("Verifying database setup...")
    logger.info(f"Database URL: {settings.database_url.replace('postgresql://', 'postgresql://***@', 1)}")

    try:
        async with engine.begin() as conn:
            # Test connection
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"✅ PostgreSQL connected: {version[:50]}...")

            # Check PostGIS extension
            result = await conn.execute(text("SELECT PostGIS_version();"))
            postgis_version = result.scalar()
            logger.info(f"✅ PostGIS enabled: {postgis_version}")

            # Check tables exist
            result = await conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name;
                """)
            )
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = ["alerts", "fields", "recommendations", "sensor_readings", "zones", "chat_messages"]
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                logger.warning(f"⚠️  Missing tables: {missing_tables}")
                logger.warning("   Run: python scripts/init_database.py")
                return False
            else:
                logger.info(f"✅ All tables exist: {', '.join(tables)}")
                return True

    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        logger.error("   Make sure PostgreSQL is running:")
        logger.error("   docker-compose up -d postgres")
        return False
    finally:
        await close_db()


async def main() -> None:
    """Main verification function."""
    success = await verify_database()
    
    if success:
        logger.info("\n🎉 Database setup is complete and ready to use!")
        sys.exit(0)
    else:
        logger.error("\n❌ Database setup needs attention. See errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

