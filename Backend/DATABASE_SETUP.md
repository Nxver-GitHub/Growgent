# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL with PostGIS for the Growgent backend.

---

## Quick Start (Docker - Recommended)

### 1. Start PostgreSQL with Docker Compose

```bash
cd Backend
docker-compose up -d postgres
```

This will:
- Start PostgreSQL 15 with PostGIS extension
- Create database `growgent`
- Expose port 5432
- Automatically enable PostGIS extension

### 2. Verify Database is Running

```bash
docker-compose ps
```

You should see `growgent-postgres` running.

### 3. Initialize Database Tables

```bash
# Activate virtual environment
.\venv\Scripts\activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac

# Run initialization script
python scripts/init_database.py
```

This will:
- Enable PostGIS extension
- Create all database tables (Field, SensorReading, Recommendation, Alert)
- Set up indexes and relationships

### 4. (Optional) Create Initial Migration

```bash
# Create initial Alembic migration
python scripts/create_migration.py "Initial schema"

# Apply migration
python scripts/run_migrations.py
```

---

## Manual Setup (Without Docker)

### 1. Install PostgreSQL with PostGIS

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Or use: `choco install postgresql postgis` (if using Chocolatey)

**macOS:**
```bash
brew install postgresql postgis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis postgresql-15-postgis-3
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE growgent;

# Connect to new database
\c growgent

# Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Exit
\q
```

### 3. Update Environment Variables

Create `Backend/.env.local`:

```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/growgent
ENVIRONMENT=development
DEBUG=true
```

### 4. Initialize Database

```bash
python scripts/init_database.py
```

---

## Database Connection String Format

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Examples:
- Local: `postgresql://postgres:postgres@localhost:5432/growgent`
- Docker: `postgresql://postgres:postgres@localhost:5432/growgent` (same, port forwarded)
- Remote: `postgresql://user:pass@db.example.com:5432/growgent`

---

## Verify Setup

### Check Database Connection

```bash
# Using psql
psql -U postgres -d growgent -c "\dt"

# Should show tables:
# - fields
# - sensor_readings
# - recommendations
# - alerts
```

### Check PostGIS Extension

```bash
psql -U postgres -d growgent -c "SELECT PostGIS_version();"
```

Should return PostGIS version (e.g., "3.4 USE_GEOS=1 USE_PROJ=1").

### Test from Python

```python
from app.database import engine
from sqlalchemy import text

async with engine.begin() as conn:
    result = await conn.execute(text("SELECT version();"))
    print(result.scalar())
```

---

## Common Commands

### Docker Compose Commands

```bash
# Start database
docker-compose up -d postgres

# Stop database
docker-compose stop postgres

# View logs
docker-compose logs -f postgres

# Restart database
docker-compose restart postgres

# Remove database (WARNING: deletes all data)
docker-compose down -v
```

### Database Management

```bash
# Connect to database
psql -U postgres -d growgent

# List all tables
\dt

# Describe a table
\d fields

# View all data in a table
SELECT * FROM fields;

# Exit psql
\q
```

### Alembic Migrations

```bash
# Create new migration
python scripts/create_migration.py "Description of changes"

# Apply all pending migrations
python scripts/run_migrations.py upgrade head

# Rollback one migration
python scripts/run_migrations.py downgrade -1

# View migration history
alembic history

# View current revision
alembic current
```

---

## Troubleshooting

### Connection Refused

**Error**: `connection refused` or `could not connect to server`

**Solutions**:
1. Check PostgreSQL is running: `docker-compose ps`
2. Check port 5432 is not in use: `netstat -an | findstr 5432` (Windows)
3. Verify connection string in `.env.local`

### PostGIS Extension Error

**Error**: `extension "postgis" does not exist`

**Solutions**:
1. Ensure you're using PostGIS-enabled image: `postgis/postgis:15-3.4`
2. Manually enable: `CREATE EXTENSION postgis;` in psql
3. Check PostGIS is installed: `SELECT PostGIS_version();`

### Authentication Failed

**Error**: `password authentication failed`

**Solutions**:
1. Check password in `.env.local` matches Docker Compose
2. Default Docker password: `postgres`
3. Reset password: `ALTER USER postgres WITH PASSWORD 'newpassword';`

### Port Already in Use

**Error**: `port 5432 is already allocated`

**Solutions**:
1. Stop existing PostgreSQL: `docker-compose down`
2. Change port in `docker-compose.yml`: `"5433:5432"`
3. Update `DATABASE_URL` to use new port

---

## Database Schema

The database includes these tables:

### `fields`
- Stores agricultural field information
- Includes PostGIS geometry for spatial queries
- Fields: id, farm_id, name, crop_type, area_hectares, location_geom

### `sensor_readings`
- IoT sensor data (moisture, temperature, pH)
- Linked to fields via foreign key
- Fields: id, field_id, sensor_id, moisture_percent, temperature, ph, reading_timestamp

### `recommendations`
- Agent-generated irrigation recommendations
- Fields: id, field_id, agent_type, action, title, reason, confidence, accepted

### `alerts`
- System alerts and notifications
- Fields: id, field_id, agent_type, severity, message, acknowledged

All tables include:
- UUID primary keys
- `created_at` and `updated_at` timestamps
- Proper indexes for performance

---

## Production Considerations

### Security

1. **Change default password**:
   ```bash
   ALTER USER postgres WITH PASSWORD 'strong_password';
   ```

2. **Use environment variables** for database URL (never commit `.env.local`)

3. **Restrict network access** in production (use firewall rules)

4. **Enable SSL** for remote connections:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/growgent?sslmode=require
   ```

### Performance

1. **Connection pooling**: Already configured in `database.py`
2. **Indexes**: Automatically created on foreign keys and frequently queried columns
3. **PostGIS indexes**: Created automatically for spatial columns

### Backup

```bash
# Backup database
pg_dump -U postgres growgent > backup.sql

# Restore database
psql -U postgres growgent < backup.sql
```

---

## Next Steps

1. ✅ Database is running
2. ✅ Tables are created
3. 🔄 Test API endpoints (they should work now!)
4. 🔄 Add sample data (optional)

---

## Quick Reference

| Task | Command |
|------|---------|
| Start DB | `docker-compose up -d postgres` |
| Stop DB | `docker-compose stop postgres` |
| Init DB | `python scripts/init_database.py` |
| Connect | `psql -U postgres -d growgent` |
| View Tables | `\dt` (in psql) |
| Create Migration | `python scripts/create_migration.py "message"` |
| Run Migrations | `python scripts/run_migrations.py` |

---

**Ready to go!** Your PostgreSQL database is set up and ready to store user data. 🚀





