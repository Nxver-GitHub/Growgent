# Growgent Data Implementation Plan
Version: 2025-11-08

Author: Max + team
Scope: California farms; irrigation scheduling under drought, wildfire, and PSPS

Status: Draft – validated against current API docs where possible (sources cited). Any items marked “uncertain” indicate endpoints that may vary by utility or require discovery.

---

## 0) Objectives and guiding constraints

- Provide timely, credible inputs for:
  - Irrigation scheduling and water metrics (ET0/ETo, precip, wind, RH, temp)
  - Fire risk context (Red Flag Warnings, active fire perimeters)
  - PSPS shutoff anticipation (utility outage/PSPS polygons)
  - Vegetation condition/consumptive use (NDVI, ET actual)
- Prioritize open/free, documented APIs with stable schemas.
- Cache aggressively; normalize to PostGIS for spatial joins with fields.
- Keep licensing compliant: ODbL (OSM), API ToS (OpenET, CIMIS), US Gov public data (NWS/NOAA).
- **Backend Implementation**: Data ingestion and processing will be handled by the FastAPI backend, leveraging PostgreSQL with PostGIS for efficient spatial queries and data storage.

---

## 1) Data sources selected (validated)

1. Weather forecasts and ET0/ETo
   - Open-Meteo Forecast API with ET₀ FAO-56 variables (no key)
     - Access/Cost: Free, no key; rate limits apply.
     - Variables include hourly temperature, RH, wind, precipitation, ET₀ FAO-56; daily ET₀ also available.
     - Docs: Ensemble/Forecast variables list includes ET₀; model updates and availability documented.
     - Sources:
       - Open-Meteo Ensemble docs (variables incl. ET₀): https://open-meteo.com/en/docs/ensemble-api
       - Model updates/availability: https://open-meteo.com/en/docs/model-updates
     - Quality: Good global coverage; consistent JSON; not an official US agency but widely used; transparent model status (see model updates).
     - Notes: Use as fast, keyless baseline feed for ET₀ and met forcing.

   - NOAA/NWS Weather.gov API (official US forecasts + alerts)
     - Access/Cost: Free; requires User-Agent header; reasonable rate limits.
     - Endpoints:
       - Points → Grid discovery: https://api.weather.gov/points/{lat},{lon}
       - Forecast/forecastHourly/forecastGridData links from points
       - Active alerts (GeoJSON/CAP): https://api.weather.gov/alerts/active with filters
     - Docs: https://www.weather.gov/documentation/services-web-api
     - Quality: Official US source; provides Red Flag Warnings via Alerts; strong reliability.
     - Notes: Use for official alerts and a second met source; respect rate limits and cache.

   - CIMIS (California Irrigation Management Information System) – Station and Spatial ETo
     - Access/Cost: Free; requires AppKey registration.
     - Station weather + ETo; Spatial CIMIS: daily ETo 2-km statewide (ASCE-PM).
     - API entry: http://et.water.ca.gov/Rest/Index (via CA Open Data catalog)
     - Docs/overview:
       - CIMIS site: https://cimis.water.ca.gov/
       - CA Open Data entry (API): https://data.ca.gov/dataset/cimis-weather-station-spatial-cimis-data-web-api
       - Spatial ETo maps: https://data.ca.gov/dataset/cimis-spatial-eto-maps
     - Quality: Gold standard for CA irrigation; station representativeness matters; Spatial ETo fills gaps.
     - Notes: Pull nearest station ETo daily; optionally compare with Spatial CIMIS at field centroid.

   - NASA POWER (optional fallback for agro meteorology, solar)
     - Access/Cost: Free; REST.
     - Useful for solar radiation and agro variables if needed.
     - Docs: https://power.larc.nasa.gov (not re-validated here; use as secondary)

2. Fire risk and activity
   - NWS Red Flag Warnings and related fire-weather products
     - Source: Weather.gov Alerts API (CAP/GeoJSON).
     - Docs: https://www.weather.gov/documentation/services-web-api and NWS Fire Weather directives/spec.
     - Policy docs (specifications for RFW/FWW): NWSI 10-401 (PDF): https://www.weather.gov/media/directives/010_pdfs/pd01004001curr.pdf
     - Quality: Official; consistent nationwide; includes polygons/areas and metadata.

   - Active fire perimeters and incidents (USGS/NIFC/Esri FeatureServers)
     - Access: Public FeatureServer endpoints vary by year/provider; quality operational.
     - Status: **UNCERTAIN ENDPOINT**. A current public FeatureServer for “active fire perimeters” must be identified (Esri-hosted services are common). This endpoint is critical for real-time fire context.
     - Notes: Once a layer is chosen, query as GeoJSON (where=1=1, f=geojson). Cache aggressively. The discovered URL should be stored in `Backend/app/config.py`.

   - National/Regional Fire Weather program references
     - National AOP 2025: https://www.weather.gov/media/fire/2025_National_AOP_V2_signed_swb_sp.pdf
     - Local AOP examples confirm RFW criteria practices (context only):
       - Example: Southern New England AOP 2025: https://www.weather.gov/media/aly/FireWX/Southern%20New%20England%20Annual%20Fire%20Weather%20Operating%20Plan%20.docx.pdf

3. Utility PSPS (Public Safety Power Shutoff)
   - Utilities (PG&E, SCE, SDG&E) outage/PSPS maps frequently backed by ArcGIS FeatureServer.
   - Access/Cost: Public status pages; endpoints change; rate-limited/brittle.
   - Status: **UNCERTAIN ENDPOINT**. Endpoint discovery required (browser DevTools on official outage/PSPS map pages) to extract concrete FeatureServer URLs.
   - Approach: Build a utility-layer adapter that accepts a FeatureServer base URL per utility; normalize schema. Discovered URLs should be stored in `Backend/app/config.py`.
   - Caution: Terms of Use; implement exponential backoff and robust error handling.

4. Vegetation and consumptive use (ET actual)
   - OpenET API (field-scale ET a/ETc products)
     - Access/Cost: Free with account; quotas apply (100 queries/month, area and complexity limits).
     - Docs: https://etdata.org/api-info/ and API reference https://openet.gitbook.io
     - Quality: Multi-model ET; monthly (2000–present) and daily (rolling since 2016); strong for irrigation accounting.
     - Notes: Excellent for historical benchmarking, season totals, and validation of recommendations. Cache summaries per field-week or month.

   - Google Earth Engine NDVI (used within MCP)
     - Access: Requires GEE account and scripts; integrated within a dedicated MCP server.
     - Status: No direct public API link; GEE scripts are used to process and extract NDVI data per field.
     - Notes: Prioritize OpenET for ET actual. GEE for NDVI provides valuable crop health context.

5. Basemaps and geospatial context
   - Mapbox tiles (basemaps, directions)
     - Access/Cost: Freemium; key required.
     - Use: Frontend visualization (Mapbox GL JS).
   - PostGIS holds field polygons and joins to all above.

---

## 2) Data model (PostgreSQL + PostGIS)

The database schema is designed for efficient storage and retrieval of agricultural data, with a strong emphasis on geospatial capabilities provided by PostGIS. All tables include `created_at` and `updated_at` timestamps for auditing.

- `fields`
  - `id` (UUID PK)
  - `farm_id` (UUID FK, for multi-tenancy)
  - `name` (TEXT, e.g., "North Field 1")
  - `crop_type` (TEXT, e.g., "Alfalfa", "Almonds")
  - `irrigation_method` (TEXT, e.g., "Drip", "Sprinkler")
  - `area_hectares` (NUMERIC)
  - `location_geom` (GEOMETRY(Polygon, 4326), stores field boundaries)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `gist (location_geom)`, `btree (farm_id)`

- `weather_hourly`
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `timestamp` (TIMESTAMPTZ)
  - `t2m` (NUMERIC, temperature at 2m)
  - `rh` (NUMERIC, relative humidity)
  - `wind_speed_10m` (NUMERIC, wind speed at 10m)
  - `precipitation` (NUMERIC, in mm)
  - `et0` (NUMERIC, reference evapotranspiration in mm)
  - `source` (TEXT ENUM: 'open_meteo', 'nws_grid')
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Unique constraint: `(field_id, timestamp, source)`
  - Indexes: `btree (field_id, timestamp)`

- `eto_daily`
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `date` (DATE)
  - `eto_mm` (NUMERIC, daily reference evapotranspiration in mm)
  - `source` (TEXT ENUM: 'cimis_station', 'cimis_spatial', 'open_meteo')
  - `distance_km` (NUMERIC, nullable, distance to CIMIS station)
  - `station_id` (TEXT, nullable, CIMIS station ID)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Unique constraint: `(field_id, date, source)`
  - Indexes: `btree (field_id, date)`

- `nws_alerts`
  - `id` (TEXT PK, from CAP ID)
  - `event` (TEXT, e.g., "Red Flag Warning")
  - `severity` (TEXT, e.g., "Moderate", "Severe")
  - `starts_at` (TIMESTAMPTZ)
  - `ends_at` (TIMESTAMPTZ)
  - `sent_at` (TIMESTAMPTZ)
  - `polygon_geom` (GEOMETRY(MultiPolygon, 4326), alert area)
  - `properties` (JSONB, full CAP message properties)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `gist (polygon_geom)`

- `fire_perimeters`
  - `id` (TEXT PK, from provider)
  - `agency` (TEXT, e.g., "CALFIRE", "USFS")
  - `updated_at` (TIMESTAMPTZ)
  - `fire_name` (TEXT, nullable)
  - `geom` (GEOMETRY(MultiPolygon, 4326), fire perimeter)
  - `properties` (JSONB, additional provider-specific data)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `gist (geom)`

- `psps_events`
  - `id` (TEXT PK, from utility)
  - `utility` (TEXT ENUM: 'PGE', 'SCE', 'SDGE')
  - `status` (TEXT ENUM: 'planned', 'active', 'restoring', 'completed')
  - `starts_at` (TIMESTAMPTZ)
  - `ends_at` (TIMESTAMPTZ, nullable)
  - `geom` (GEOMETRY(MultiPolygon, 4326), affected area)
  - `properties` (JSONB, additional utility-specific data)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `gist (geom)`

- `et_actual_monthly`
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `year_month` (DATE, first day of month)
  - `et_mm` (NUMERIC, actual evapotranspiration in mm)
  - `source` (TEXT ENUM: 'openet')
  - `model` (TEXT, e.g., "ensemble", "ssebop")
  - `qa` (JSONB, quality assurance metadata)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Unique constraint: `(field_id, year_month, source, model)`
  - Indexes: `btree (field_id, year_month)`

- `sensor_readings` (Aligned with `Backend/DATABASE_SETUP.md`)
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `sensor_id` (TEXT, unique identifier for the sensor)
  - `moisture_percent` (NUMERIC)
  - `temperature` (NUMERIC)
  - `ph` (NUMERIC, nullable)
  - `reading_timestamp` (TIMESTAMPTZ)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `btree (field_id, reading_timestamp)`

- `recommendations` (Aligned with `Backend/DATABASE_SETUP.md`)
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `agent_type` (TEXT ENUM: 'fire_adaptive_irrigation', 'water_efficiency', 'psps_anticipation')
  - `action` (TEXT, e.g., "Irrigate 10mm", "Delay Irrigation")
  - `title` (TEXT)
  - `reason` (TEXT)
  - `confidence` (NUMERIC, 0-100)
  - `accepted` (BOOLEAN, default FALSE)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `btree (field_id, created_at)`

- `alerts` (Aligned with `Backend/DATABASE_SETUP.md`)
  - `id` (UUID PK)
  - `field_id` (UUID FK)
  - `agent_type` (TEXT ENUM: 'fire_adaptive_irrigation', 'water_efficiency', 'psps_anticipation', 'system')
  - `severity` (TEXT ENUM: 'info', 'warning', 'critical')
  - `message` (TEXT)
  - `acknowledged` (BOOLEAN, default FALSE)
  - `created_at` (TIMESTAMPTZ, default NOW())
  - `updated_at` (TIMESTAMPTZ, default NOW())
  - Indexes: `btree (field_id, created_at)`

---

## 3) Ingestion and update cadence

Data ingestion will be managed by dedicated background tasks within the FastAPI backend, ensuring timely updates and adherence to API rate limits.

- **Open-Meteo forecast**: Hourly pull per field centroid every 1–3 hours. Cache TTL 10–15 minutes for API calls. Store next 7–10 days of hourly data.
- **NWS points→grid**: Cache points discovery for 7 days. Hourly forecasts 1–3 hours. Alerts poll every 2–5 minutes during demo, otherwise 5–10 minutes.
- **CIMIS**:
  - **Station ETo**: Daily pull after 12:00 local time when day’s ETo is posted. Backfill on first run. Choose nearest representative station (store distance/station_id).
  - **Spatial ETo**: Daily raster/statistic at field centroid or area-weighted mean. For hackathon, centroid sample is sufficient.
- **Fire perimeters**: Poll chosen FeatureServer every 5–10 minutes. Deduplicate by provider ID + `updated_at`.
- **PSPS**: Poll utility FeatureServers every 5 minutes. Implement exponential backoff on errors.
- **OpenET**: Batch job daily to fetch last 7–30 days of monthly/daily summaries for target fields (stay under quotas). Store monthly aggregates.

---

## 4) API integration details and consistency checks

All external API integrations will be handled by dedicated MCP (Micro-Agent Communication Protocol) servers, as outlined in `Growgent_Technical_PRD.md`, ensuring modularity and fault isolation. Pydantic models will be used for schema validation of all incoming API responses.

4.1 Open-Meteo
- Endpoint pattern (forecast):
  - `GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,et0_fao_evapotranspiration&timezone=UTC`
- Variable availability:
  - ET₀ FAO-56 is available in hourly/daily variable lists. If unavailable at a coordinate/model, fall back to CIMIS/NASA POWER.
- Model timing/status:
  - Refer to model updates page for awareness of delays: https://open-meteo.com/en/docs/model-updates
- Cost/accessibility: Free, no key.

4.2 NWS Weather.gov
- Discovery:
  - `GET https://api.weather.gov/points/{lat},{lon}` → returns JSON with office, gridX, gridY, and URLs for forecast endpoints.
- Alerts:
  - `GET https://api.weather.gov/alerts/active?point={lat},{lon}` or filter `event=Red%20Flag%20Warning`
- Requirements:
  - Must set `User-Agent` header per docs. Rate limits are undisclosed; cache aggressively.
- Docs: https://www.weather.gov/documentation/services-web-api
- Official fire-weather product specifications:
  - NWSI 10-401 PDF: https://www.weather.gov/media/directives/010_pdfs/pd01004001curr.pdf

4.3 CIMIS
- Web API entry:
  - Docs and access via CA Open Data link; API base documented at http://et.water.ca.gov/Rest/Index (AppKey required).
  - Catalog: https://data.ca.gov/dataset/cimis-weather-station-spatial-cimis-data-web-api
- Overview/operations:
  - https://cimis.water.ca.gov/
  - Spatial ETo maps dataset: https://data.ca.gov/dataset/cimis-spatial-eto-maps
- Variables:
  - Station: measured (temp/RH/wind/solar), derived (ETo). Spatial: ETo and Rs.
- Quality: High for CA; choose station by microclimate; Spatial 2-km grid derived from GOES + models.
- Cost: Free with key.

4.4 OpenET
- API info: https://etdata.org/api-info/
- API reference: https://openet.gitbook.io
- Quotas (free):
  - 100 queries/month; <=50k acres/query; polygon count limits; Earth Engine compute unit limits.
- Data availability:
  - Monthly 2000–present; daily rolling since 2016; recent data may revise up to ~6 months.

4.5 Fire perimeters (USGS/NIFC/Esri) – endpoint selection
- Status: **UNCERTAIN ENDPOINT**. Not a single canonical URL; commonly public ArcGIS FeatureServer layers for current-year perimeters.
- Plan: Identify an active, public FeatureServer during setup; example pattern:
  - `GET {FEATURESERVER_BASE}/query?where=1%3D1&outFields=*&f=geojson&outSR=4326&returnGeometry=true`
- Accessibility: Free; rate-limited by Esri hosting. Cache. The discovered URL should be stored in `Backend/app/config.py`.

4.6 PSPS FeatureServers (PG&E/SCE/SDG&E)
- Status: **UNCERTAIN ENDPOINT**. Undocumented public endpoints behind utility outage maps; subject to change.
- Plan:
  - Discover concrete URLs via browser DevTools.
  - Normalize to unified schema; store polygons + attributes. Discovered URLs should be stored in `Backend/app/config.py`.
- Accessibility/Cost: Public; unstable. Cache + backoff.

---

## 5) Data processing logic (Agent-driven)

Data processing is orchestrated by the LangGraph-based agents, as detailed in `Growgent_Technical_PRD.md`.

- **ET reference vs. actual**:
  - **Reference ET**: Prefer CIMIS ETo (station if representative; else Spatial). Store in `eto_daily`.
  - **ET₀ from Open-Meteo**: Used by the Fire-Adaptive Irrigation Agent for near-real-time hourly scheduling and same-day adjustments. Cross-check daily against CIMIS ETo.
  - **ET actual (OpenET)**: Used by the Water Efficiency Agent for monthly baselines, season totals, metrics, and calibration (Kc estimation where applicable).

- **Irrigation recommendation core (Fire-Adaptive Irrigation Agent)**:
  - Computes daily water balance per field: `ΔS = (ETc − P_eff) − irrigation_applied`
  - `ETc = Kc × ET_ref`. `Kc` is determined by crop stage (configurable tables); optionally refined using OpenET historical ETa ratios.
  - `P_eff` (effective precipitation): Empirical function (e.g., FAO-56) or simple cap per soil storage.
  - **Anticipate PSPS**: If forecast PSPS window overlaps next 24–48 hours and a Red Flag Warning is present, the agent generates a pre-irrigation recommendation within soil capacity constraints.

- **Fire/alerts (Utility Shutoff Anticipation Agent & Fire-Adaptive Irrigation Agent)**:
  - Joins NWS alert polygons with field polygons.
  - Computes distances to active fire perimeters.
  - Derives risk scores for UI display and informs irrigation decisions.

- **Spatial simplifications for hackathon**:
  - Use centroid sampling for raster-based sources (Spatial CIMIS) initially.
  - Area-weighted zonal statistics are considered for "Phase 2" if time permits.

---

## 6) Update scheduling

All data ingestion and processing tasks will be managed by an async task runner (e.g., APScheduler or a background job worker like Celery/RQ) within the FastAPI backend.

- `weather.open_meteo_forecast`: Cron `*/30 * * * *` (every 30 minutes)
- `nws.alerts_poll`: Cron `*/5 * * * *` (every 5 minutes)
- `cimis.daily_eto`: Cron `15 13 * * *` America/Los_Angeles (daily at 1:15 PM PST, adjust when daily ETo is posted)
- `fire.perimeters_poll`: Cron `*/10 * * * *` (every 10 minutes)
- `psps.poll_all`: Cron `*/5 * * * *` (every 5 minutes)
- `openet.monthly_backfill`: Cron `5 2 * * *` (daily at 2:05 AM) and throttled to respect quotas.

---

## 7) FastAPI service contracts (selected)

These API endpoints are exposed by the FastAPI backend and consumed by the frontend, as described in `Growgent_Technical_PRD.md`.

- `GET /api/weather/hourly?field_id=...&hours=72`
  - Merges Open-Meteo (primary) and optionally NWS grid data; returns aligned hourly series with source tags.
- `GET /api/eto/daily?field_id=...&days=30`
  - Returns daily ETo with source preference: `cimis_station > cimis_spatial > open_meteo`.
- `GET /api/alerts/fire?field_id=...`
  - Returns active NWS alerts intersecting field; includes Red Flag Warnings.
- `GET /api/fire/perimeters?bbox=...`
  - Returns active fire perimeters within bbox; provider metadata.
- `GET /api/psps/active?field_id=...`
  - Returns active/planned PSPS polygons intersecting or within buffer.
- `GET /api/et/monthly?field_id=...&months=24`
  - Returns OpenET monthly ETa with model metadata; cached.
- `POST /api/recommendation`
  - Input: `field_id`, optional constraints (soil capacity, irrigation window), nowcast horizon
  - Output: schedule, volumes, rationale (ET forecast, PSPS overlap, Red Flag).
- `GET /api/metrics/water`
  - Returns water efficiency metrics for a field or farm.
- `GET /api/metrics/fire-risk`
  - Returns fire risk metrics for a field or farm.
- `GET /api/alerts`
  - Returns all active alerts, with filtering options.

---

## 8) Frontend overlays (Mapbox GL JS)

The frontend will utilize Mapbox GL JS for interactive geospatial visualization, as specified in `Growgent_Technical_PRD.md`.

- **Mapbox GL layers**:
  - `fields` (fill + outline)
  - `NWS Alerts` polygons (semi-transparent, categorized)
  - `Fire perimeters` (stroke + hatch)
  - `PSPS polygons` (per utility color)
  - `Choropleth by NDVI/ET gap` (optional, derived from GEE/OpenET data)

- **Tiles**:
  - Optionally add NDFD WMS layers (temperature/precip) if desired; not necessary for MVP.

Docs:
- NDFD WMS usage: https://digital.weather.gov/staticpages/mapservices.php

---

## 9) Cost, accessibility, quality summary

- **Open-Meteo**: Free/no key; reliable; ET₀ provided; excellent for hackathon.
- **NWS Weather.gov**: Free; official; requires User-Agent; robust; alerts (RFW).
- **CIMIS**: Free with key; station + Spatial ETo; CA-specific gold standard.
- **OpenET**: Free with quotas; high-quality ET actual; ideal for historical/monthly benchmarking.
- **Fire perimeters**: Public FeatureServers; quality operational; **endpoint discovery needed**.
- **PSPS**: Public utility maps/FeatureServers; brittle; **endpoint discovery needed**; cache heavily.
- **Mapbox**: Freemium; key required for frontend visualization.
- **Google Earth Engine**: Requires GEE account for NDVI processing within MCP.

---

## 10) Risks and mitigations

- **PSPS endpoints change**:
  - Mitigation: Abstract adapters; discover at runtime from `Backend/app/config.py`; fallbacks: scrape summary status if polygons unavailable.
- **Rate limits / quotas**:
  - Mitigation: In-memory + Redis caching; batch field requests; nightly ETL; exponential backoff; implement `httpx` with retry logic.
- **Spatial representativeness (CIMIS station)**:
  - Mitigation: Choose nearest with metadata; compare with Spatial CIMIS; store `distance_km`.
- **ET₀ inconsistency across sources**:
  - Mitigation: Define precedence; store per-source values; present provenance in UI.
- **Uncertain FeatureServer URLs**:
  - Mitigation: Prioritize manual discovery using browser DevTools on official utility/fire map pages. Implement robust error handling and logging for these endpoints.

---

## 11) Implementation tasks

- **DB migrations**: Create tables and indexes as listed using Alembic.
- **Secrets**: App keys (CIMIS, Mapbox, OpenET) stored securely in environment variables (e.g., `.env.local` for development, Google Secret Manager for production). Add `User-Agent` header for NWS requests.
- **Services**:
  - Use `httpx.AsyncClient` with retry/backoff for all external API calls.
  - Implement MCP servers as separate Python modules within `Backend/app/mcp/`.
  - Utilize `WATCHFILES_IGNORE` to avoid `venv` reload loops in development.
- **ETL jobs**: Implement as background tasks using an async task runner (e.g., APScheduler) with structured logging.
- **Schema validation**: Use Pydantic models for validating all incoming data from external APIs and internal data structures.

---

## 12) Example request templates

- **Open-Meteo**
  - `GET https://api.open-meteo.com/v1/forecast?latitude=38.5&longitude=-121.5&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,et0_fao_evapotranspiration&timezone=UTC`

- **NWS alerts (Red Flag Warning near point)**
  - `GET https://api.weather.gov/alerts/active?event=Red%20Flag%20Warning&point=38.5,-121.5`
  - Headers: `User-Agent: Growgent (growgent.example, contact@example.com)`

- **CIMIS Spatial ETo (documentation/catalog)**
  - Start at http://et.water.ca.gov/Rest/Index (AppKey required); dataset catalog:
    - https://data.ca.gov/dataset/cimis-weather-station-spatial-cimis-data-web-api

- **OpenET monthly timeseries (via API docs)**
  - See https://openet.gitbook.io/docs/quick-start for endpoint and auth; adhere to quotas from https://etdata.org/api-info/

- **Esri FeatureServer pattern (for fire perimeters/PSPS)**
  - `GET {FEATURESERVER_BASE}/query?where=1%3D1&outFields=*&f=geojson&outSR=4326&returnGeometry=true`

---

## 13) Testing and validation

- **Unit tests**: For parsing/normalizing API responses, CRS correctness, geometry intersections, and individual agent logic.
- **Integration tests**: Verify communication between MCPs, agents, and the database.
- **Contract tests**: Use tools like Schemathesis for `Weather.gov` OpenAPI schema checks and internal API contracts.
- **Backfills**: Implement deterministic replays for fixed days; compare ETo totals across sources (with defined tolerances).
- **Performance**: Verify database indexes; use `EXPLAIN ANALYZE` on spatial joins to optimize queries.

---

## 14) Compliance and licensing

- **NWS data**: US Gov public domain; include attribution where appropriate.
- **CIMIS**: Free with key; follow API ToS; acknowledge DWR/CIMIS.
- **OpenET**: Follow API ToS and quotas; include attribution.
- **Mapbox**: Follow attribution requirements.
- **OSM data (if used)**: ODbL attribution.

---

## 15) Items requiring discovery (critical for MVP)

- **Specific FeatureServer URL(s) for**:
  - **Active fire perimeters**: A current, public ArcGIS FeatureServer layer (e.g., from USGS, NIFC, CALFIRE) for real-time fire perimeters.
  - **PSPS/outage polygons**: For major California utilities (PG&E, SCE, SDG&E). These are typically found by inspecting network requests (browser DevTools) on their official outage/PSPS map pages.

**Action**: These URLs must be discovered and added to `Backend/app/config.py` before full real-time fire and PSPS functionality can be implemented.

---

## Sources (validated)

- Open-Meteo Ensemble/variables (incl. ET₀) and model updates:
  - https://open-meteo.com/en/docs/ensemble-api
  - https://open-meteo.com/en/docs/model-updates
- NWS Weather.gov API documentation:
  - https://www.weather.gov/documentation/services-web-api
- NWS Fire Weather specification (NWSI 10-401, PDF):
  - https://www.weather.gov/media/directives/010_pdfs/pd01004001curr.pdf
- NDFD WMS and metadata (optional map layers):
  - https://digital.weather.gov/staticpages/mapservices.php
  - https://www.weather.gov/gis/NDFD_metadata.html
- CIMIS overview and API catalog:
  - https://cimis.water.ca.gov/
  - https://data.ca.gov/dataset/cimis-weather-station-spatial-cimis-data-web-api
  - Spatial ETo maps dataset: https://data.ca.gov/dataset/cimis-spatial-eto-maps
- OpenET API:
  - https://etdata.org/api-info/
  - https://openet.gitbook.io

Notes:
- NASA POWER not re-validated here; retain as optional fallback.
- Fire perimeter and PSPS FeatureServer endpoints are intentionally left “to be discovered” and can change; design adapters accordingly.

---