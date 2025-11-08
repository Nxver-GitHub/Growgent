# Growgent Backend - Quick Start Guide

Get the Growgent backend running in 5 minutes!

---

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for PostgreSQL)
- Git

---

## Step 1: Install Dependencies

```bash
cd Backend

# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Start PostgreSQL Database

```bash
# Start PostgreSQL with Docker Compose
docker-compose up -d postgres

# Wait a few seconds for database to be ready
# Check status:
docker-compose ps
```

You should see `growgent-postgres` with status "Up".

---

## Step 3: Initialize Database

```bash
# Initialize database tables and PostGIS extension
python scripts/init_database.py
```

Expected output:
```
✅ Database initialized successfully!
   - PostGIS extension enabled
   - All tables created
```

---

## Step 4: Start the API Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Step 5: Test the API

### Test Health Endpoint

```bash
# Using curl
curl http://localhost:8000/health

# Or open in browser
# http://localhost:8000/health
```

### Test Agent Recommendation

```bash
# Generate a recommendation
curl -X POST "http://localhost:8000/api/agents/irrigation/recommend" \
  -H "Content-Type: application/json" \
  -d '{"field_id": "123e4567-e89b-12d3-a456-426614174000"}'
```

---

## Verify Everything Works

### 1. Check Database Tables

```bash
# Connect to database
docker exec -it growgent-postgres psql -U postgres -d growgent

# List tables
\dt

# Should show:
# - fields
# - sensor_readings
# - recommendations
# - alerts

# Exit
\q
```

### 2. Check API Documentation

Open http://localhost:8000/docs in your browser. You should see:
- All API endpoints
- Request/response schemas
- Try it out functionality

### 3. Run Tests

```bash
# Run agent tests (no database needed)
pytest tests/test_agents_irrigation_simple.py -v

# All 8 tests should pass ✅
```

---

## Troubleshooting

### Database Connection Error

**Error**: `connection refused` or `password authentication failed`

**Solution**:
1. Check PostgreSQL is running: `docker-compose ps`
2. Wait a few seconds after starting: `docker-compose up -d postgres`
3. Check logs: `docker-compose logs postgres`

### Port Already in Use

**Error**: `port 5432 is already allocated`

**Solution**:
1. Stop existing PostgreSQL: `docker-compose down`
2. Or change port in `docker-compose.yml`

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'asyncpg'`

**Solution**:
```bash
pip install asyncpg geoalchemy2
# Or reinstall all dependencies:
pip install -r requirements.txt
```

---

## Next Steps

1. ✅ **Backend is running** - API is accessible at http://localhost:8000
2. ✅ **Database is ready** - All tables created
3. ✅ **Agent is working** - Can generate recommendations
4. 🔄 **Add sample data** (optional) - Create test fields and sensor readings
5. 🔄 **Connect frontend** (Agent 3) - Frontend can now call these APIs

---

## Useful Commands

```bash
# Database
docker-compose up -d postgres          # Start database
docker-compose stop postgres           # Stop database
docker-compose logs -f postgres        # View logs
docker-compose down                    # Stop and remove containers

# Database Management
python scripts/init_database.py       # Initialize database
python scripts/create_migration.py "message"  # Create migration
python scripts/run_migrations.py      # Run migrations

# API Server
uvicorn app.main:app --reload          # Start with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000  # Start on all interfaces

# Testing
pytest tests/ -v                      # Run all tests
pytest tests/test_agents_irrigation_simple.py -v  # Run agent tests
```

---

## Environment Variables

Create `Backend/.env.local` (optional - defaults work for development):

```bash
# Database (defaults work with Docker Compose)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/growgent

# Environment
ENVIRONMENT=development
DEBUG=true

# Optional API Keys (not needed for development)
# NOAA_API_KEY=
# ANTHROPIC_API_KEY=
# MAPBOX_TOKEN=
```

---

**You're all set!** 🎉

The backend is ready to:
- Store user data (fields, sensor readings, recommendations, alerts)
- Generate irrigation recommendations via the Fire-Adaptive Irrigation Agent
- Serve data via REST API endpoints
- Handle multiple users (via farm_id and field relationships)





