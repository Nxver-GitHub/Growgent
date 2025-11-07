# Growgent – Technical Product Requirements Document (PRD)

## Challenge Focus: Smart Water & Irrigation Planning Under Fire Stress

---

## 1. Executive Summary

Growgent is an open-source, agentic platform for climate-adaptive irrigation and wildfire management. It leverages multi-agent systems and modern web infrastructure to help California farmers make resilient irrigation decisions during drought, utility shutoffs (PSPS), and wildfire risks. Every part of the codebase, integrations, service orchestration, and dashboard design is crafted to meet sponsor and event guidelines, using high-quality, well-documented open-source frameworks and practices.

---

## 2. Technical Architecture & Stack

### Modern Open-Source Stack

#### Frontend
- Framework: Next.js (React 18+), App Router (app/ directory)
- Language: TypeScript (full type safety, leverages TSConfig strict mode)
- Styling: Tailwind CSS (utility-based, rapid prototyping; optional integration with Chakra UI for accessible design)
- GIS & Maps: Mapbox GL JS, @react-map-gl (display irrigation zones, fire zones, PSPS overlays)
- Data Fetching: React Query (TanStack Query) – for robust, cached API calls; handles loading/error states cleanly
- State Management: Zustand or React Context API – lightweight, easy global state sync
- Forms: React Hook Form + Zod (schema validation, async checks)
- Testing: Jest + React Testing Library (unit, integration); Storybook (UI component testing)
- Build & Deployment: Vercel (instant preview deployments, auto CI)

#### Backend
- Framework: FastAPI (Python 3.11+, type hinting enforced, async support)
- Agent Orchestration: LangGraph (multi-agent flows, agent communication protocols)
- Data Store: PostgreSQL (Docker), spatial extension with PostGIS (field/fire zone geometry queries)
- API Spec: OpenAPI 3.1 auto-generated docs (/docs endpoint on FastAPI)
- Cache: Redis (optional, for alert deduplication and fast sensor polling)
- MCP Integration: Custom MCP servers (Python, Docker, JSON-RPC 2.0 compliant)
- Testing: pytest for backend logic, API contract tests via Schemathesis/openapi-cli
- DevOps: Docker Compose for local, Helm charts/YAML for Kubernetes

#### Integrations & Services
- Data APIs: NOAA (weather/fire), PG&E/SDG&E/SCE (PSPS mappings), Google Earth Engine (NDVI)
- CRM/Chat: Salesforce Agentforce (REST webhook for Q&A, demo org for CRM sync)
- Auth (Optional): NextAuth.js (frontend), OAuth2 via Salesforce or Google (backend)
- Other: GitHub Actions (CI/CD), Prettier, Black, Flake8 (enforced code formatting)

#### Documentation & Communication
- Docs: Docusaurus (if time), otherwise README.md and /docs folder with API, MCP, architecture and code conventions
- Code Comments: Every function/class/agent has meaningful docstrings (Python) and JSDoc (TypeScript)
- Issue Templates: GitHub issues and PR templates set up for bugs/features

---

## 3. Agent Detail & API Flows

#### Agents
- Fire-Adaptive Irrigation Agent:
  - Runs as LangGraph node; pulls from MCPS & field context.
  - Calls: /api/agents/irrigation/recommend; responds with schedule, reason, confidence.
  - Data: Calls NOAA, PG&E, Google Earth Engine NDVI, local moisture sensors.
  - Outputs to frontend dashboard and CRM.

- Water Efficiency Agent:
  - Compares recommended vs. actual irrigation, tracks savings.
  - Calls: /api/agents/water/metrics; outputs season summary, can email PDF (report gen).

- Utility Shutoff Anticipation Agent:
  - Monitors PSPS events via utility API polling.
  - Sends push/email alerts and pre-irrigation autoschedule; calls /api/agents/psps/alert.

Each agent exposes REST endpoints and shares context/states over MCP for modular upgrades.

#### APIs
- /api/recommendation – POST: field, sensor, fire context; GET: latest, historical
- /api/fields – GET: all field zones, geometry, sensors
- /api/fire-risk – GET: risk zones, forecast, utility overlays
- /api/agents/* – GET/POST: agent-specific endpoints with unified response contracts
- /api/metrics – GET: farm season summary, water/fire metrics
- /api/alerts – GET/POST: fetch, create, acknowledge

#### MCP Servers
- Weather: Polls OpenWeather, NOAA, mock data fallback
- Fire Risk: Calls NOAA and Cal Fire, overlays with Mapbox
- Utility: PG&E and related APIs, returns active/predicted shutoffs
- Sensor: Local or simulated; CSV/JSON or LoRaWAN integration possible

All MCP servers run in individual Docker containers for modular testing and rapid replacement/upgrades.

---

## 4. Software Engineering Best Practices

Code Quality
- Use strict linting (eslint for JS/TS, flake8 for Python).
- 80+% unit test coverage.
- PRs require passing tests and clean code checks.
- Functions/classes are single-purpose; code split by feature.

Documentation
- Docstrings/JSDoc required for all public code.
- API endpoints fully documented in OpenAPI and inline README sections.
- MCP server contracts and JSON data structures explicitly defined in /docs.

Merge & CI/CD
- Feature branches always rebase/merge off latest main.
- No package updates outside of explicit PRs with upgrade/test logs.
- Automated CI pipeline checks for conflicts, unused deps, type errors.

Open Source
- AGPL v3 license in root directory.
- Code of Conduct and contributing guidelines.
- All data/algorithms open and reproducible.

Security
- Handle all sensitive API keys/tokens via environment variables.
- Regular dependency vulnerability scanning.
- Sanitize all frontend inputs, validate all backend data.

Dev Collaboration
- Modular codebase; /frontend, /backend, /agents, /mcp, /infra.
- PR reviews required from at least one non-author team member.
- Active issues/ticketing, clear tagging (bug, feature, enhancement).

---

## 5. Deliverables (Hackathon)

- Backend agentic service (FastAPI, LangGraph, Postgres, MCP servers, full REST/OpenAPI docs).
- Frontend dashboard (Next.js/TypeScript/Tailwind/Mapbox, agent cards, metrics, responsive design).
- Salesforce chat integration (Agentforce, webhook, demo org).
- Demo scenario for wildfires + drought + PSPS event, end-to-end working chain.
- Full open-source repo with README, dev setup, architecture diagrams, API and MCP docs.

---

## 6. Sponsor & Event Alignment

- Salesforce: Agentforce demo integration, possible Data Cloud backend
- Google (Earth Engine): NDVI/field health, satellite overlays
- PG&E, SDG&E, SCE: Real utility-mapping APIs for shutoff resilience
- NOAA: Fire forecasts (environmental openness)
- LangChain & MCP: Multi-agent, open interoperability

---

## 7. Quality Assurance & Scaling

- Automated CI with GitHub Actions
- E2E tests (Playwright/Cypress) run nightly
- Performance monitoring (Lighthouse, unoptimized images)
- Code reviews to ensure merge stability and minimize bugs
- Staging branch for hackathon tests; main branch auto-deploys previews

---

## 8. UX/UI Principles

- Use scalable color system for risk/alert communication (green, amber, red, slate)
- Accessible by default (contrast, keyboard nav, ARIA labels)
- Mobile-first for field crew; desktop-rich analytics for managers
- Interactive Mapbox layers for spatial decisions
- Clear, actionable agent recommendations (not just passive data dumps)
- All user-facing strings localizable (future internationalization)

---

This PRD is ready for direct reference by coding agents, IDEs, and full-stack developers. It details how every API, service, framework, and open-source tool is used, how software standards are enforced, and how the codebase is maintained, documented, and scaled for long-term stability.
