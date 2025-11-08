# Testing Agent 2 Components (Water Efficiency & PSPS Anticipation)

## Quick Start

### 1. Ensure Database is Running

```bash
# Check if PostgreSQL container is running
docker ps --filter "name=growgent-postgres"

# If not running, start it
cd Backend
docker-compose up -d postgres

# Wait for database to be ready (about 10 seconds)
```

### 2. Initialize Database (if not already done)

```bash
cd Backend
python scripts/init_database.py
```

This will:
- Enable PostGIS extension
- Create all tables (fields, sensor_readings, recommendations, alerts)

### 3. Run Quick Smoke Tests

```bash
cd Backend
pytest tests/test_agent2_quick.py -v
```

These tests verify basic functionality:
- ✅ Water Efficiency Agent can process fields
- ✅ PSPS Agent can process fields  
- ✅ Metrics Service calculates correctly
- ✅ Alert Service creates/retrieves alerts

### 4. Run Integration Tests

```bash
# Water Efficiency Agent tests
pytest tests/test_integration_agents.py::TestWaterEfficiencyAgentIntegration -v

# PSPS Agent tests
pytest tests/test_integration_agents.py::TestPSPSAgentIntegration -v
```

### 5. Run Full E2E Tests

```bash
# Water Efficiency E2E
pytest tests/test_e2e_agent2.py::TestWaterEfficiencyE2E -v

# PSPS E2E
pytest tests/test_e2e_agent2.py::TestPSPSE2E -v

# All Agent 2 E2E tests
pytest tests/test_e2e_agent2.py -v -m e2e
```

## Test Files Overview

### `test_agent2_quick.py`
**Purpose**: Quick smoke tests to verify basic functionality  
**Duration**: ~5-10 seconds  
**Use Case**: Verify setup is correct before running full test suite

**Tests**:
- `test_water_efficiency_agent_basic` - Agent processes field and calculates metrics
- `test_psps_agent_basic` - Agent detects PSPS events
- `test_metrics_service_basic` - Service calculates water metrics
- `test_alert_service_basic` - Service creates and retrieves alerts

### `test_integration_agents.py`
**Purpose**: Integration tests for agents with database  
**Duration**: ~30-60 seconds  
**Use Case**: Verify agents work correctly with real database

**Test Classes**:
- `TestWaterEfficiencyAgentIntegration` - Full agent workflow tests
- `TestPSPSAgentIntegration` - PSPS detection and alerting tests

### `test_e2e_agent2.py`
**Purpose**: End-to-end tests from API to database  
**Duration**: ~1-2 minutes  
**Use Case**: Verify complete workflows including API endpoints

**Test Classes**:
- `TestWaterEfficiencyE2E` - Complete water efficiency workflow
- `TestPSPSE2E` - Complete PSPS workflow
- `TestMetricsE2E` - Metrics API workflows
- `TestAlertOrchestrationE2E` - Multi-agent alert orchestration

## What Each Test Verifies

### Water Efficiency Agent Tests

✅ **Basic Functionality**
- Agent can process a field
- Calculates water saved, efficiency, cost savings
- Generates drought stress score

✅ **Milestone Alerts**
- Creates alerts when water savings reach milestones
- Tracks cumulative savings

✅ **API Integration**
- Metrics available via `/api/metrics/water` endpoint
- Response schema validation
- Multiple time periods (season, month, week, all)

### PSPS Anticipation Agent Tests

✅ **Basic Functionality**
- Detects PSPS events from MCP
- Identifies affected fields using geospatial queries
- Tracks seen events to avoid duplicates

✅ **Alert Generation**
- Creates CRITICAL alerts for active shutoffs
- Creates WARNING alerts for predicted shutoffs
- Links alerts to affected fields

✅ **Pre-Irrigation Recommendations**
- Generates PRE_IRRIGATE recommendations before shutoffs
- Only for predicted events (36-48 hours ahead)
- Prevents duplicate recommendations

## Expected Test Results

### ✅ Success Indicators

When tests pass, you should see:
```
✅ Water Efficiency Agent: Calculated 15000L saved
✅ PSPS Agent: Found 2 affected fields
✅ Metrics Service: 85.5% efficiency, 15000L saved
✅ Alert Service: Created and retrieved alert <uuid>
```

### ⚠️ Common Issues

**Database Connection Errors**
```
Error: ModuleNotFoundError: No module named 'sqlalchemy'
Solution: Install dependencies: pip install -r requirements.txt
```

**Database Not Initialized**
```
Error: relation "fields" does not exist
Solution: Run: python scripts/init_database.py
```

**PostGIS Not Enabled**
```
Error: function st_intersects(geometry, geometry) does not exist
Solution: Database should auto-enable PostGIS, check docker logs
```

## Running Tests in CI/CD

```yaml
# Example GitHub Actions workflow
- name: Start PostgreSQL
  run: |
    cd Backend
    docker-compose up -d postgres
    sleep 15  # Wait for database to be ready

- name: Initialize Database
  run: |
    cd Backend
    python scripts/init_database.py

- name: Run Agent 2 Tests
  run: |
    cd Backend
    pytest tests/test_agent2_quick.py -v
    pytest tests/test_integration_agents.py -v
    pytest tests/test_e2e_agent2.py -v -m e2e
```

## Test Data Isolation

Tests use:
- **Test farm_id**: `test-farm-001`
- **Test field**: Created fresh for each test
- **Auto-cleanup**: Each test rolls back database changes

This ensures:
- Tests don't interfere with each other
- No manual cleanup needed
- Tests can run in parallel (with proper database setup)

## Debugging Failed Tests

### Enable Verbose Output
```bash
pytest tests/test_agent2_quick.py -v -s
```

### Run Single Test
```bash
pytest tests/test_agent2_quick.py::test_water_efficiency_agent_basic -v
```

### Check Database State
```bash
# Connect to database
docker exec -it growgent-postgres psql -U postgres -d growgent

# Check tables
\dt

# Check test data
SELECT * FROM fields WHERE farm_id = 'test-farm-001';
SELECT * FROM alerts WHERE field_id IN (SELECT id FROM fields WHERE farm_id = 'test-farm-001');
```

## Next Steps

Once tests pass:
1. ✅ Water Efficiency Agent is working
2. ✅ PSPS Anticipation Agent is working
3. ✅ All services are integrated
4. ✅ API endpoints are functional
5. 🎯 Ready for production deployment!





