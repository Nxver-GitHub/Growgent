# Data Collection Strategy Based on User Inputs

## Overview

This document outlines what datasets should be connected and when data collection should be triggered based on user inputs in the Growgent platform.

---

## User Inputs That Trigger Data Collection

### 1. **Field Creation** (Primary Trigger)
When a user creates a field, the following inputs trigger data collection:

**Required Inputs:**
- `farm_id`: Farm identifier
- `name`: Field name
- `crop_type`: Type of crop (e.g., "corn", "wheat", "tomatoes")
- `area_hectares`: Field area in hectares
- `location_geom`: **CRITICAL** - Geographic location (latitude, longitude) as PostGIS Point

**Optional Inputs:**
- `notes`: Additional field metadata

**Why Location Matters:**
The `location_geom` (latitude/longitude) is the **primary key** that determines:
- Which weather data to fetch
- Which fire risk zones apply
- Which utility service area (PSPS) covers the field
- Which satellite imagery to retrieve
- Which sensor networks are nearby

---

## Datasets to Connect Based on Field Location

### ✅ **Currently Implemented (via MCP Servers)**

#### 1. **Weather Data** (`WeatherMCP`)
**Trigger:** Field creation with `location_geom`
**Data Sources:**
- **OpenWeather API** (Primary)
  - 7-day weather forecast
  - Temperature, humidity, wind speed, precipitation
  - Current conditions
- **NOAA API** (Alternative/Fallback)
  - Extended forecasts
  - Historical weather patterns
  - Fire weather conditions

**When to Fetch:**
- Immediately when field is created
- Every 6 hours (via scheduler) for irrigation agent
- On-demand when user requests weather data

**Data Collected:**
```json
{
  "current": {
    "temperature": 25.5,
    "humidity": 45,
    "wind_speed": 12.3,
    "precipitation": 0
  },
  "forecast": [
    {
      "date": "2024-01-15",
      "temperature": 28.0,
      "precipitation": 5.2,
      "humidity": 50
    }
  ]
}
```

#### 2. **Fire Risk Zones** (`FireRiskMCP`)
**Trigger:** Field creation with `location_geom`
**Data Sources:**
- **NOAA Fire Weather API**
  - Fire danger ratings
  - Fire weather zones
  - Red flag warnings
- **Cal Fire API** (California-specific)
  - Active fire perimeters
  - Fire risk assessments
  - Evacuation zones

**When to Fetch:**
- Immediately when field is created
- Every 4 hours (via scheduler) for fire risk monitoring
- When fire risk alerts are triggered

**Data Collected:**
```json
{
  "zones": [
    {
      "zone_id": "zone-123",
      "risk_score": 0.75,
      "risk_level": "high",
      "geometry": {...},  // GeoJSON polygon
      "last_updated": "2024-01-15T10:00:00Z"
    }
  ],
  "active_fires": [],
  "evacuation_areas": []
}
```

#### 3. **PSPS (Power Shutoff) Data** (`PSPSMCP`)
**Trigger:** Field creation with `location_geom`
**Data Sources:**
- **PG&E API** (Pacific Gas & Electric)
  - Active shutoffs
  - Predicted shutoffs (48-hour forecast)
  - Affected areas (GeoJSON polygons)
- **SDG&E API** (San Diego Gas & Electric)
- **SCE API** (Southern California Edison)

**When to Fetch:**
- Immediately when field is created (check if currently affected)
- Every 30 minutes (via scheduler) for PSPS monitoring
- When PSPS alerts are triggered

**Data Collected:**
```json
{
  "active_shutoffs": [
    {
      "id": "psps-001",
      "utility": "PG&E",
      "start_time": "2024-01-15T08:00:00Z",
      "estimated_end_time": "2024-01-16T08:00:00Z",
      "affected_customers": 15000,
      "counties": ["Sonoma", "Napa"],
      "geometry": {...}  // GeoJSON polygon
    }
  ],
  "predicted_shutoffs": [
    {
      "id": "psps-002",
      "predicted_start_time": "2024-01-17T10:00:00Z",
      "confidence": 0.85,
      "reason": "High fire risk conditions forecast"
    }
  ]
}
```

#### 4. **IoT Sensor Data** (`SensorMCP`)
**Trigger:** Field creation (links sensors to field)
**Data Sources:**
- **LoRaWAN Sensor Networks**
  - Soil moisture sensors
  - Temperature sensors
  - pH sensors
  - Battery level monitoring
- **Field-specific sensor IDs**

**When to Fetch:**
- Continuously (sensors push data)
- Every hour for latest readings
- On-demand when agent needs current conditions

**Data Collected:**
```json
{
  "sensor_id": "sensor-001",
  "field_id": "field-uuid",
  "moisture_percent": 35.5,
  "temperature": 22.3,
  "ph": 6.8,
  "battery_level": 85,
  "signal_strength": -120,
  "reading_timestamp": "2024-01-15T10:30:00Z"
}
```

---

### 🔄 **Should Be Added (Not Yet Implemented)**

#### 5. **Satellite Imagery & NDVI** (`SatelliteMCP`)
**Trigger:** Field creation with `location_geom` + `area_hectares`
**Data Sources:**
- **Google Earth Engine API**
  - NDVI (Normalized Difference Vegetation Index)
  - Crop health monitoring
  - Vegetation density
  - Historical satellite imagery
- **Sentinel-2 / Landsat**
  - Multi-spectral imagery
  - Crop growth stages
  - Stress detection

**When to Fetch:**
- Weekly when field is created
- Every 2 weeks for crop health monitoring
- On-demand for detailed analysis

**Data Needed:**
- Field boundary polygon (from `location_geom` + `area_hectares`)
- Crop type (for crop-specific analysis)
- Historical baseline (for comparison)

**Data Collected:**
```json
{
  "ndvi": 0.78,
  "crop_health_score": 0.85,
  "vegetation_density": "high",
  "last_image_date": "2024-01-10",
  "historical_trend": {
    "30_days_ago": 0.72,
    "60_days_ago": 0.68
  }
}
```

#### 6. **Soil Data** (`SoilMCP`)
**Trigger:** Field creation with `location_geom`
**Data Sources:**
- **USDA Soil Survey (SSURGO)**
  - Soil type classification
  - Soil moisture capacity
  - Drainage characteristics
  - Organic matter content
- **State agricultural extension services**
  - Regional soil data
  - Crop-specific soil requirements

**When to Fetch:**
- Once when field is created (static data)
- Updated annually or when soil tests are performed

**Data Collected:**
```json
{
  "soil_type": "Loam",
  "moisture_capacity": 0.35,
  "drainage": "moderate",
  "organic_matter_percent": 2.5,
  "ph_range": [6.0, 7.0],
  "crop_suitability": {
    "corn": "excellent",
    "wheat": "good",
    "tomatoes": "moderate"
  }
}
```

#### 7. **Water Rights & Restrictions** (`WaterRightsMCP`)
**Trigger:** Field creation with `location_geom` + `farm_id`
**Data Sources:**
- **State Water Resources Control Board** (California)
  - Water rights allocations
  - Usage restrictions
  - Drought declarations
- **Local water districts**
  - Irrigation schedules
  - Water allocation limits

**When to Fetch:**
- Once when field is created
- Monthly for restriction updates
- When drought alerts are issued

**Data Collected:**
```json
{
  "water_rights_id": "WR-12345",
  "allocation_liters_per_year": 5000000,
  "usage_this_year": 2500000,
  "restrictions": {
    "current": "none",
    "drought_level": "moderate"
  },
  "irrigation_schedule": {
    "allowed_days": ["Monday", "Wednesday", "Friday"],
    "allowed_hours": "6:00 AM - 10:00 AM"
  }
}
```

#### 8. **Historical Crop Data** (`CropHistoryMCP`)
**Trigger:** Field creation with `crop_type` + `location_geom`
**Data Sources:**
- **USDA Crop Progress Reports**
  - Regional crop growth stages
  - Typical harvest dates
  - Yield expectations
- **Agricultural extension services**
  - Crop-specific best practices
  - Regional growing calendars

**When to Fetch:**
- Once when field is created (baseline data)
- Seasonally for crop-specific recommendations

**Data Collected:**
```json
{
  "crop_type": "corn",
  "typical_growing_season": {
    "planting": "April - May",
    "harvest": "September - October"
  },
  "regional_yield_expectation": 8.5,  // tons/hectare
  "typical_water_requirement": 500,  // mm/season
  "growth_stages": ["seedling", "vegetative", "flowering", "maturity"]
}
```

---

## Data Collection Triggers & Timing

### **Immediate (On Field Creation)**
When a user creates a field, these datasets should be fetched immediately:

1. ✅ Weather forecast (7-day)
2. ✅ Fire risk zones (current)
3. ✅ PSPS status (active + predicted)
4. ⏳ Soil data (SSURGO lookup)
5. ⏳ Water rights (if available)
6. ⏳ Historical crop data (baseline)

### **Scheduled (Automatic)**
Via the agent scheduler:

1. ✅ **Weather**: Every 6 hours (irrigation agent)
2. ✅ **PSPS**: Every 30 minutes (PSPS agent)
3. ✅ **Fire Risk**: Every 4 hours (fire risk monitoring)
4. ✅ **Sensor Data**: Continuously (IoT push) + hourly pull
5. ⏳ **Satellite/NDVI**: Every 2 weeks (crop health)
6. ⏳ **Water Restrictions**: Monthly (compliance check)

### **Event-Driven (On-Demand)**
Triggered by specific events:

1. **User Request**: When user views field details
2. **Agent Decision**: When agent needs current data for recommendation
3. **Alert Trigger**: When conditions change significantly
4. **Manual Refresh**: User clicks "Refresh Data"

---

## Implementation Recommendations

### **Phase 1: Current (MVP) ✅**
- Weather MCP (OpenWeather/NOAA)
- Fire Risk MCP (NOAA/Cal Fire)
- PSPS MCP (PG&E/SDG&E/SCE)
- Sensor MCP (LoRaWAN)

### **Phase 2: High Priority (Next)**
1. **Satellite/NDVI MCP**
   - Critical for crop health monitoring
   - Enables visual field analysis
   - Requires Google Earth Engine API key

2. **Soil Data MCP**
   - Improves irrigation recommendations
   - One-time fetch per field
   - Uses public USDA SSURGO data

### **Phase 3: Enhanced Features**
3. **Water Rights MCP**
   - Compliance monitoring
   - Regional restrictions
   - Requires state/local API access

4. **Crop History MCP**
   - Baseline comparisons
   - Regional benchmarks
   - Uses public USDA data

---

## Data Collection Service Pattern

### **Recommended Architecture:**

```python
# When field is created
async def on_field_created(field: Field, db: AsyncSession):
    """Trigger data collection for new field."""
    
    # Extract location
    lat, lon = extract_location(field.location_geom)
    
    # Fetch all relevant datasets
    tasks = [
        weather_mcp.get_forecast(lat, lon),
        fire_risk_mcp.get_fire_risk_zones(lat, lon),
        psps_mcp.get_predicted_shutoffs(lat, lon),
        soil_mcp.get_soil_data(lat, lon),  # Future
        satellite_mcp.get_ndvi(field.boundary),  # Future
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Store results in database
    await store_field_data(field.id, results, db)
```

---

## Summary

**Current Status:**
- ✅ 4 datasets connected (Weather, Fire Risk, PSPS, Sensors)
- ⏳ 4 datasets recommended (Satellite, Soil, Water Rights, Crop History)

**Key Insight:**
The `location_geom` (latitude/longitude) is the **primary trigger** for data collection. When a user creates a field with a location, the system should automatically fetch all relevant environmental and regulatory data for that geographic area.

**Next Steps:**
1. Implement Satellite/NDVI MCP for crop health
2. Add Soil Data MCP for improved recommendations
3. Create data collection service to trigger on field creation
4. Add caching layer to avoid redundant API calls

