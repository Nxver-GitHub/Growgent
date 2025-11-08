# End-to-End Tests for Agent 2 Components

## Overview

Comprehensive end-to-end tests have been created for all Agent 2 (Data Intelligence) components. These tests verify the complete workflow from API endpoints through services and agents to the database.

## Prerequisites

1. **Docker PostgreSQL Database Running**
   ```bash
   docker ps --filter "name=growgent-postgres"
   # Should show container running on port 5433
   ```

2. **Database Initialized**
   ```bash
   cd Backend
   python scripts/init_database.py
   ```

3. **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

## Test Files

### `test_e2e_agent2.py`
Complete end-to-end tests covering:

- **Water Efficiency E2E** (`TestWaterEfficiencyE2E`)
  - Full workflow: Recommendations → Agent → Metrics API → Alerts
  - API-to-service flow validation
  - Multiple period testing

- **PSPS E2E** (`TestPSPSE2E`)
  - PSPS detection and alert workflow
  - Alert creation via API and verification
  - Pre-irrigation recommendations

- **Metrics E2E** (`TestMetricsE2E`)
  - Water metrics with recommendations
  - Farm summary across multiple fields
  - Fire risk metrics with accepted recommendations

- **Alert Orchestration E2E** (`TestAlertOrchestrationE2E`)
  - Multi-agent alert creation
  - Filtering and pagination

## Running the Tests

### Run All E2E Tests
```bash
cd Backend
pytest tests/test_e2e_agent2.py -v -m e2e
```

### Run Specific Test Class
```bash
pytest tests/test_e2e_agent2.py::TestWaterEfficiencyE2E -v
pytest tests/test_e2e_agent2.py::TestPSPSE2E -v
pytest tests/test_e2e_agent2.py::TestMetricsE2E -v
```

### Run Specific Test
```bash
pytest tests/test_e2e_agent2.py::TestWaterEfficiencyE2E::test_water_efficiency_full_workflow -v
```

### Run with Coverage
```bash
pytest tests/test_e2e_agent2.py --cov=app --cov-report=html -m e2e
```

## Test Configuration

The tests use the actual PostgreSQL database configured in `app/config.py`:
- **Database URL**: `postgresql://postgres:postgres@localhost:5433/growgent`
- **PostGIS**: Enabled for spatial queries
- **Test Isolation**: Each test rolls back changes automatically

## Test Fixtures

- `db_session`: Async database session (rolls back after each test)
- `sample_field`: Pre-created test field with sample data

## What the Tests Verify

### ✅ Water Efficiency Workflow
1. Creates Fire-Adaptive Irrigation recommendations
2. Runs Water Efficiency Agent
3. Verifies metrics calculation via API
4. Checks for milestone alerts

### ✅ PSPS Anticipation Workflow
1. Runs PSPS Agent to detect shutoffs
2. Verifies alerts created via API
3. Checks pre-irrigation recommendations

### ✅ Metrics API Workflow
1. Tests all metrics endpoints (`/api/metrics/water`, `/api/metrics/water/summary`, `/api/metrics/fire-risk`)
2. Validates response schemas
3. Verifies calculated values

### ✅ Alert Orchestration
1. Tests multi-agent alert creation
2. Verifies filtering and pagination
3. Tests alert acknowledgment flow

## Expected Results

All tests should pass when:
- Docker PostgreSQL is running
- Database is initialized with tables
- All dependencies are installed
- Virtual environment is activated (if using one)

## Troubleshooting

### Database Connection Issues
```bash
# Check if database is running
docker ps --filter "name=growgent-postgres"

# Check database logs
docker logs growgent-postgres

# Restart database if needed
docker-compose restart postgres
```

### Import Errors
```bash
# Ensure you're in the Backend directory
cd Backend

# Activate virtual environment (if using one)
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Test Failures
- Check that database tables exist: `python scripts/init_database.py`
- Verify database connection: Check `DATABASE_URL` in `.env.local`
- Check test logs for specific error messages

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run E2E Tests
  run: |
    docker-compose up -d postgres
    sleep 10  # Wait for database to be ready
    pytest tests/test_e2e_agent2.py -v -m e2e
```

## Next Steps

1. ✅ All Agent 2 components implemented
2. ✅ Integration tests created
3. ✅ End-to-end tests created
4. ✅ Database fixtures configured
5. 🎯 **Ready to run tests against PostgreSQL database**





