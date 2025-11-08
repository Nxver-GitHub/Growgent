# API Keys Setup Guide for Growgent Backend

## Quick Answer: **NO API Keys Required for Development!**

The Fire-Adaptive Irrigation Agent works **perfectly without any API keys** in development mode. All MCP servers automatically use realistic mock data when:
- No API key is provided, OR
- Environment is set to `development` (default)

---

## API Keys Overview

### ✅ **Required: NONE** (for MVP/Development)

The agent is designed to work with **zero API keys** using mock data fallbacks.

### 🔑 **Optional: For Production with Real Data**

If you want to use real API data instead of mock data, you can optionally add these keys:

#### 1. **NOAA API Key** (Optional)
- **Purpose**: Weather forecasts and fire risk data
- **Used by**: Weather MCP, Fire Risk MCP
- **Get it**: https://www.ncdc.noaa.gov/cdo-web/token (free)
- **Fallback**: Mock data (realistic weather/fire scenarios)
- **Environment Variable**: `NOAA_API_KEY`

#### 2. **OpenWeather API Key** (Optional)
- **Purpose**: Weather forecasts (alternative to NOAA)
- **Used by**: Weather MCP
- **Get it**: https://openweathermap.org/api (free tier available)
- **Fallback**: Mock data
- **Note**: Currently uses `NOAA_API_KEY` (can be separated later)
- **Environment Variable**: `OPENWEATHER_API_KEY` (not yet implemented)

#### 3. **Anthropic API Key** (Optional)
- **Purpose**: Advanced LangGraph agent features (if using LLM-based decisions)
- **Used by**: Agent orchestration (future enhancement)
- **Get it**: https://console.anthropic.com/
- **Fallback**: Rule-based logic (current implementation doesn't need it)
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Status**: **NOT REQUIRED** - Agent uses rule-based logic, not LLM

#### 4. **Mapbox Token** (Frontend - Agent 3)
- **Purpose**: Map rendering in frontend
- **Used by**: Frontend dashboard (not backend agent)
- **Get it**: https://account.mapbox.com/access-tokens/ (free tier available)
- **Environment Variable**: `MAPBOX_TOKEN`
- **Status**: **Agent 1 doesn't need this** (Agent 3's responsibility)

---

## How Mock Data Works

All MCP servers have intelligent mock data fallbacks:

### Weather MCP
- **Mock provides**: 7-day forecast with realistic temperature, humidity, wind, precipitation
- **Triggers**: No `NOAA_API_KEY` OR `environment=development`

### PSPS MCP
- **Mock provides**: Realistic PSPS predictions (36-48 hours ahead)
- **Triggers**: `environment=development` (always in dev)

### Sensor MCP
- **Mock provides**: Realistic sensor readings with gradual moisture decrease
- **Triggers**: `environment=development` (always in dev)

### Fire Risk MCP
- **Mock provides**: Fire risk zones with GeoJSON polygons
- **Triggers**: No `NOAA_API_KEY` OR `environment=development`

---

## Setup Instructions

### For Development (No Keys Needed)

1. **Create `.env.local` file** in `Backend/` directory:
```bash
# Backend/.env.local
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/growgent
```

2. **That's it!** The agent will use mock data automatically.

### For Production (Optional Real Data)

1. **Create `.env.local`** with optional keys:
```bash
# Backend/.env.local
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/growgent

# Optional: Real API data
NOAA_API_KEY=your_noaa_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  # Only if using LLM features
```

2. **Set environment variables** (or use `.env.local`):
```bash
export NOAA_API_KEY=your_key
export ENVIRONMENT=production
```

---

## Verification

To verify the agent works without keys:

1. **Run the agent** (no keys needed):
```python
from app.agents import fire_adaptive_irrigation_agent
from uuid import uuid4

state = await fire_adaptive_irrigation_agent.recommend(field_id=uuid4())
print(state.recommended_action)  # Will work with mock data!
```

2. **Check logs** - You'll see:
```
INFO: Using mock weather data
INFO: Using mock PSPS data
INFO: Using mock sensor data
INFO: Using mock fire risk data
```

---

## Summary

| API Key | Required? | Purpose | Fallback |
|---------|-----------|---------|----------|
| NOAA API Key | ❌ No | Real weather/fire data | ✅ Mock data |
| OpenWeather Key | ❌ No | Real weather forecasts | ✅ Mock data |
| Anthropic Key | ❌ No | LLM features (not used) | ✅ Rule-based logic |
| Mapbox Token | ❌ No | Frontend maps (Agent 3) | N/A |
| Database URL | ✅ Yes | PostgreSQL connection | N/A |

**Bottom Line**: The Fire-Adaptive Irrigation Agent works perfectly with **zero API keys** in development mode. All external data sources have intelligent mock fallbacks that provide realistic test scenarios.

---

## Next Steps

1. ✅ **Agent works now** - No keys needed for development
2. 🔄 **Set up PostgreSQL** - Only database connection needed
3. 🔑 **Add keys later** (optional) - For production with real data

