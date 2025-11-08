--- GEMINI.md ---
# Gemini Development Guide for Growgent

This document outlines the core principles and rules for AI-assisted development on the Growgent project, derived from the `.cursorrules` file.

## Core Mandate: 95% Certainty Threshold

**I must not implement any code changes unless I am 95% certain that I understand:**
1.  The user's request and intent.
2.  The exact implementation procedure.
3.  The impact of the changes on the existing codebase (no breaking changes).
4.  The testing strategy and all relevant edge cases.

If I am not 95% certain, I will **stop** and ask clarifying questions, providing at least three specific options.

## Code Style and Quality

### General
-   **Clarity and Maintainability:** Code should be easy to read and understand.
-   **Documentation:** Add JSDoc/docstrings to all public functions and components. Explain the "why" behind complex logic with inline comments.

### Frontend (TypeScript/React)
-   **Typing:** Strict TypeScript. No `any` types.
-   **Styling:** Use Tailwind CSS exclusively.
-   **Data Fetching:** Use React Query for all server-state management.
-   **State Management:** Use Zustand for global client-state.
-   **Forms:** Use React Hook Form with Zod for validation.
-   **Naming:**
    -   Components: `PascalCase.tsx`
    -   Hooks/Functions: `camelCase.ts`
    -   Other files: `kebab-case.ts`

### Backend (Python/FastAPI)
-   **Typing:** Full type hints for all functions.
-   **API:** Use FastAPI best practices, including Pydantic models for serialization and validation.
-   **Database:** Use SQLAlchemy ORM. No raw SQL.
-   **Async:** Use `async/await` for all I/O-bound operations.
-   **Naming:**
    -   Classes: `PascalCase`
    -   Functions/Variables: `snake_case`

## Testing

-   **Frontend:** Use Jest and React Testing Library. Test component rendering, user interactions, and state changes.
-   **Backend:** Use pytest. Test API endpoints, business logic, and database operations.
-   **Coverage:** Aim for 80%+ test coverage, with 100% for critical paths.

## Git and Version Control

-   **Branch Naming:** `feature/...`, `fix/...`, `refactor/...`, `docs/...`
-   **Commit Messages:** Follow the Conventional Commits specification (e.g., `feat(api): ...`, `fix(ui): ...`).

## Project Structure and Integration

I will adhere to the project structure outlined in the `.cursorrules` file, which specifies separate `frontend` and `backend` directories with clear conventions for organizing components, services, and other modules.

When adding new frontend components, my top priority is to integrate them cleanly into the existing structure. I will:
1.  Analyze the existing component hierarchy and file organization.
2.  Place new components in the appropriate directory.
3.  Reuse existing components, hooks, and styles where possible.
4.  Ensure the new component fits seamlessly into the existing UI and UX.

---
--- README.md ---

# Growgent

Open-source agentic platform for climate-adaptive irrigation and wildfire management.

## Project Structure

```
growgent/
├── frontend/          # Next.js frontend (currently Vite, migrating to Next.js)
│   ├── app/           # Next.js App Router (to be created)
│   ├── components/    # React components
│   ├── styles/        # Global styles
│   ├── public/        # Static assets
│   └── package.json
│
├── backend/            # FastAPI backend
│   ├── app/
│   │   ├── main.py     # FastAPI initialization
│   │   ├── config.py   # Settings
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # Pydantic models
│   │   ├── api/        # API routes
│   │   ├── agents/     # LangGraph agents
│   │   ├── mcp/        # MCP servers
│   │   ├── services/   # Business logic
│   │   └── utils/
│   ├── tests/          # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── Product Documents/  # Product requirements and documentation
├── Coding Agent Rules/ # Cursor and CodeRabbit configuration
└── LICENSE.md
```

## Quick Start

### Frontend (Vite - migrating to Next.js)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
docker run --name growgent-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=growgent \
  -p 5432:5432 \
  -d postgres:15
uvicorn app.main:app --reload
```

Backend API runs on `http://localhost:8000`

API documentation available at `http://localhost:8000/docs`

## Development

See `Product Documents/Growgent_Technical_PRD.md` for full technical specifications.

See `Coding Agent Rules/.cursorrules` for development guidelines and coding standards.

## License

AGPL v3 - See LICENSE.md

---
--- TODO.md ---

# Growgent Project TODO List

This document outlines the current tasks and priorities for the Growgent project, compiled from various `.md` files, with a focus on achieving MVP readiness.

## 🎯 Project Goal

Growgent is an open-source, agentic platform for climate-adaptive irrigation and wildfire management. It aims to help California farmers make resilient irrigation decisions during drought, utility shutoffs (PSPS), and wildfire risks using multi-agent systems orchestrated by LangGraph.

## 🚀 Current Status Summary

*   **Frontend:** Approximately 70% complete for MVP. Core components exist but need enhancements to match Figma design and full functionality. Critical issues include excessive re-rendering and backend connection handling. High-priority enhancements involve Mapbox integration, drag-to-reschedule for irrigation, Agentforce chat integration, and charts for water metrics. The frontend is currently using Vite but is planned to migrate to Next.js.
*   **Backend:** Implements multi-agent systems (Fire-Adaptive Irrigation, Water Efficiency, Utility Shutoff Anticipation Agents) using LangGraph, FastAPI, PostgreSQL with PostGIS, and custom MCP servers for external data. The backend seems more established, with clear architecture and development guidelines.
*   **Overall:** The project emphasizes open-source practices, strict type safety (TypeScript/Python type hints), comprehensive testing (80%+ coverage goal), and adherence to code quality standards.

---

## ✅ TODO List

### Phase 1: Critical Frontend Fixes (High Priority - Do First)

*   **Fix Excessive Re-rendering:**
    *   **Problem:** `AppContent` renders multiple times per second, causing console noise and potential performance degradation.
    *   **Solution:** Add memoization and error boundary handling in `App.tsx` (lines 48-53) and enhance error state handling in `frontend/lib/hooks/useAlerts.ts`.
    *   **Files:** `frontend/App.tsx`, `frontend/lib/hooks/useAlerts.ts`
*   **Backend Connection Handling:**
    *   **Problem:** Console shows repeated "Failed to fetch" errors when backend is offline.
    *   **Solution:** Suppress console warnings in production, add retry logic with exponential backoff, and show a connection status indicator in the header.
    *   **Files:** `frontend/lib/api.ts`, `frontend/components/AppHeader.tsx`

### Phase 2: High Priority Frontend Features

*   **FieldsMap - Mapbox Integration:**
    *   **Current State:** Placeholder UI, no actual map.
    *   **Tasks:**
        *   Install `mapbox-gl` and `@react-map-gl`.
        *   Create Mapbox GL JS map component.
        *   Add field boundary polygons (GeoJSON from API).
        *   Add sensor markers with popups.
        *   Implement NDVI heatmap overlay.
        *   Add fire risk zone layers (red/orange/yellow).
        *   Add PSPS shutoff area overlays (purple).
        *   Add irrigation recommendation pins.
        *   Implement field selection (click polygon → update sidebar).
        *   Add map controls (zoom, recenter, basemap toggle).
        *   Mobile: Full-height map with bottom sheet sidebar.
    *   **Files:** `frontend/components/FieldsMap.tsx` (complete rewrite), `frontend/lib/hooks/useMapData.ts` (new), `frontend/lib/utils/mapbox.ts` (new), `frontend/package.json` (add dependencies).
*   **IrrigationSchedule - Drag-to-Reschedule:**
    *   **Current State:** Calendar displays events, but no drag functionality.
    *   **Tasks:**
        *   Install `react-dnd` or use native HTML5 drag-drop.
        *   Make calendar events draggable.
        *   Add drop zones for each day.
        *   Show visual feedback during drag (ghost element).
        *   Validate drops (prevent dropping on PSPS windows).
        *   Call API to update recommendation on drop.
        *   Show optimistic UI updates.
        *   Handle conflicts (show error toast).
        *   Add confirmation dialog for critical changes.
    *   **Files:** `frontend/components/IrrigationSchedule.tsx`, `frontend/lib/hooks/useRecommendations.ts` (add update mutation), `frontend/package.json` (add dependencies).
*   **Chat - Agentforce Integration:**
    *   **Current State:** UI exists, but no backend connection.
    *   **Tasks:**
        *   Connect to `/api/agents/chat` endpoint.
        *   Implement message sending with loading states.
        *   Handle streaming responses (if backend supports).
        *   Add quick commands (`/weather`, `/irrigation`, `/fire-risk`, `/help`).
        *   Show action buttons in bot responses ([Accept], [View Schedule], [Details]).
        *   Add message persistence (localStorage or sessionStorage).
        *   Handle errors gracefully (show "Agent offline" message).
        *   Add typing indicators.
        *   Implement message history pagination.
    *   **Files:** `frontend/components/Chat.tsx`, `frontend/lib/hooks/useChat.ts` (enhance with API calls), `frontend/lib/api.ts`.
*   **WaterMetrics - Charts & Analytics:**
    *   **Current State:** KPI cards exist, but no charts.
    *   **Tasks:**
        *   Install `recharts`.
        *   Create water use over time chart (area chart: recommended vs. actual).
        *   Create fire risk trajectory chart (line chart).
        *   Create crop health (NDVI) trend chart.
        *   Create drought stress bar chart by week.
        *   Create agent performance table.
        *   Add date range selector (Last 30 days, Q3, Year, Custom).
        *   Implement PDF export (jsPDF or html2canvas).
        *   Implement CSV export.
        *   Implement email report functionality (optional).
    *   **Files:** `frontend/components/WaterMetrics.tsx`, `frontend/lib/hooks/useMetrics.ts` (enhance with date range), `frontend/components/charts/` (new directory), `frontend/package.json` (add dependencies).

### Phase 3: Medium Priority - Design Polish

*   **Design System Alignment:**
    *   **Tasks:** Verify exact colors from Figma, update Tailwind config, standardize spacing, border radius, shadows, and typography.
    *   **Files:** `frontend/tailwind.config.js`, `frontend/index.css`, all component files.
*   **Dashboard Hero Section:**
    *   **Tasks:** Verify hero text, CTAs, gradient colors, spacing, typography, and decorative elements match Figma.
    *   **Files:** `frontend/components/Dashboard.tsx` (hero section).
*   **Agent Status Cards:**
    *   **Tasks:** Verify all 4 cards match Figma design, ensure status indicators, metric display format, icon usage, sizing, hover states, and interactions are correct.
    *   **Files:** `frontend/components/AgentStatusCard.tsx`, `frontend/components/Dashboard.tsx`.

### Phase 4: Low Priority - Nice to Have / Optimization

*   **Settings Page Enhancement:**
    *   **Tasks:** Add Profile, Farm, Notifications, Data Privacy settings, and export data functionality.
*   **Accessibility Improvements:**
    *   **Tasks:** Add ARIA labels, ensure keyboard navigation, test with screen reader, verify color contrast, add focus indicators, add skip links.
*   **Performance Optimization:**
    *   **Tasks:** Run Lighthouse audit, implement code splitting, lazy load images, optimize bundle size, add service worker (optional).

### Phase 5: Backend & General Enhancements

*   **Type Safety:** Add strict typing throughout the frontend (address `any` types).
*   **Error Handling:** Add error boundaries and user-friendly error messages for API calls.
*   **Loading States:** Add skeleton loaders to all data-fetching components.
*   **Backend Testing:** Ensure 80%+ test coverage for backend.
*   **Documentation:** Ensure all functions, classes, and agents have meaningful docstrings (Python) or JSDoc (TypeScript).
*   **Frontend Framework Migration:** (Future) Migrate frontend from Vite to Next.js App Router.

---

## 🛠️ Technical Debt / Considerations

*   **Framework Mismatch:** Frontend is currently Vite + React, but the PRD specifies Next.js 14+ App Router. (User confirmed to ignore migration for now).
*   **Backend Status:** Backend is not currently running (connection refused errors) - *needs to be addressed for full frontend testing.*
*   **Figma Access:** Design reference available at provided Figma link.
*   **Mobile Testing:** Test on actual devices (375px, 768px, 1024px, 1920px).

---

## 🎯 Success Criteria for MVP

The frontend will be MVP-ready when:
*   All pages render without errors.
*   All components match Figma design.
*   All interactive features work (drag-drop, chat, map).
*   Mobile responsive at all breakpoints.
*   Accessibility score >95.
*   Performance score >80.
*   Component tests pass (60%+ coverage).
*   Zero TypeScript errors.

---

**Next Steps:** Start with Phase 1 (Critical Fixes), then proceed to Phase 2 (High Priority Features).

---
--- Product Documents/Growgent_Technical_PRD.md ---

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

---
--- Product Documents/UX_IMPROVEMENTS.md ---

# Growgent UX Improvements Summary

## Overview
This document outlines all user experience improvements made to the Growgent platform to enhance usability, reduce clutter, and improve overall workflow efficiency.

---

## 1. Collapsible Sidebar Navigation

### What Changed
- **Before**: Fixed-width sidebar always visible
- **After**: Fully collapsible sidebar with icon-only mode

### Features
- Click "Collapse" button to minimize sidebar to icon-only view
- Tooltips appear on hover when collapsed to show menu item names
- Badge notifications visible even in collapsed state
- Menu icon in header when sidebar is collapsed for easy expansion
- Smooth transitions between states

### Benefits
- More screen real estate for content
- Better for users with smaller displays
- Maintains navigation accessibility

---

## 2. Dismissable Alerts System

### What Changed
- **Before**: Alert cards had non-functional dismiss buttons
- **After**: Alerts can be permanently dismissed with state management

### Features
- Click "X" button to dismiss individual alerts
- "Mark All as Read" button dismisses all alerts at once
- Alert count badge updates dynamically when alerts are dismissed
- Empty state shown when all alerts cleared
- Toast notifications confirm dismissal actions

### Benefits
- Users can manage notification overload
- Clean workspace after addressing alerts
- Clear visual feedback on actions

---

## 3. Collapsible Filter Panels

### What Changed
- **Before**: Filters always visible on Irrigation Schedule page
- **After**: Toggle "Show/Hide Filters" button

### Features
- Filters hidden by default for cleaner view
- Click "Show Filters" to reveal filter options
- Close button (X) in filter panel header
- "Reset Filters" button to clear all selections

### Benefits
- Reduces visual clutter
- Focuses attention on calendar content
- Filters available when needed

---

## 4. Event Detail Modals

### What Changed
- **Before**: No detailed view for calendar events
- **After**: Click-to-open modal dialogs with full event details

### Features
- Click any calendar event to see detailed information
- Modal shows: field, time, type, alert status, duration, water volume, fire impact
- "Accept Recommendation", "Close", and action buttons
- Modal auto-closes after action
- ESC key or click outside to dismiss

### Benefits
- Better information hierarchy
- Cleaner calendar view
- Easy to take action on recommendations

---

## 5. Collapsible Map Layer Controls

### What Changed
- **Before**: Map layers always expanded, taking up map space
- **After**: Collapsible layer control panel

### Features
- Click "Map Layers" header to expand/collapse
- Chevron icon indicates state
- Minimizes to small button when collapsed
- All layer toggles accessible when open

### Benefits
- More map viewing area
- Less distraction when layers aren't being adjusted
- Professional map interface

---

## 6. Collapsible Charts and Tables

### What Changed
- **Before**: All charts and tables always visible on metrics page
- **After**: Sections can be collapsed independently

### Features
- "Performance Charts" section collapses/expands
- "Agent Performance Summary" table collapses/expands
- Chevron icons show current state
- Sections remember state during session

### Benefits
- Focus on specific data sections
- Faster page scrolling
- Better for mobile devices

---

## 7. Chat History Management

### What Changed
- **Before**: No way to clear chat history
- **After**: "Clear History" button with confirmation dialog

### Features
- "Clear History" button in header
- Alert dialog asks for confirmation before clearing
- Resets to welcome message after clearing
- Auto-scroll to bottom on new messages
- Typing indicator when bot is responding

### Benefits
- Fresh start for new conversations
- Privacy consideration
- Visual feedback on bot activity

---

## 8. Recommendation Modal System

### What Changed
- **Before**: Agent cards navigated to non-existent agent detail page
- **After**: Modal opens with detailed recommendation

### Features
- Click agent status card to see recommendation
- Shows confidence meter, reason, affected fields
- Displays water volume, duration, fire impact, water savings
- "Accept", "Dismiss", "Reschedule" actions
- Toast notifications confirm actions

### Benefits
- Quick access to recommendations
- Actionable interface
- No navigation disruption

---

## 9. Toast Notification System

### What Changed
- **Before**: No feedback on user actions
- **After**: Toast notifications for all major actions

### Features Implemented
- Success toasts: "Alert dismissed", "Settings saved", "Recommendation accepted"
- Info toasts: "Viewing data for...", "Opening documentation..."
- Export confirmations: "PDF exported", "Calendar file downloaded"
- Auto-dismiss after 3-5 seconds
- Stack multiple toasts if needed

### Benefits
- Clear feedback on every action
- Non-intrusive notifications
- Improved user confidence

---

## 10. Smart Export Buttons

### What Changed
- **Before**: Export buttons with no feedback
- **After**: Toast confirmations on all exports

### Features
- PDF Report: "PDF report generated. Check your downloads."
- CSV Export: "CSV file exported successfully."
- Email Report: "Report emailed to john@sunnydalefarm.com"
- Calendar Export: "Calendar file downloaded. Import to your calendar app."

### Benefits
- Users know action completed
- Instructions for next steps
- Professional feel

---

## 11. Settings Page with Tabs

### What Changed
- **Before**: "Coming soon" placeholder
- **After**: Full settings interface with tabbed sections

### Features
- **Profile Tab**: Name, email, phone, role
- **Farm Tab**: Farm name, location, timezone, crops, area
- **Notifications Tab**: Toggle channels (in-app, email, SMS, push), quiet hours
- **About Tab**: Version, license, documentation links, support

### Benefits
- All settings organized logically
- Easy to find specific settings
- Professional settings interface

---

## 12. Mobile Responsiveness Improvements

### What Changed
- Enhanced responsive behavior across all components

### Features
- Sidebar collapses automatically on mobile
- Bottom sheet behavior for modals on small screens
- Touch-friendly button sizes (44x44px minimum)
- Simplified layouts for narrow screens
- Horizontal scrolling for tables on mobile

---

## 13. Keyboard Accessibility

### Features Added
- ESC key closes modals
- Enter key sends chat messages
- Tab navigation through all interactive elements
- Focus visible on all buttons and inputs
- ARIA labels on all controls

---

## 14. Empty States

### What Changed
- **Before**: No messaging when lists were empty
- **After**: Friendly empty state messages

### Examples
- Alerts page: "No alerts to display. All caught up! 🎉"
- Calendar: "No events" placeholder
- Clear visual feedback

---

## 15. Loading States

### Features Added
- Chat typing indicator (animated dots)
- Skeleton loaders ready for async data
- Disabled states on buttons during actions

---

## Summary of UX Principles Applied

1. **Progressive Disclosure**: Show only what's needed, hide complexity
2. **Feedback**: Every action has visual confirmation
3. **Reversibility**: Most actions can be undone or dismissed
4. **Consistency**: Similar patterns used throughout (modals, toasts, collapses)
5. **Accessibility**: WCAG compliant, keyboard navigable, screen reader friendly
6. **Responsiveness**: Works on desktop, tablet, and mobile
7. **Performance**: Lazy loading, collapsible sections reduce initial render
8. **Clarity**: Clear labels, descriptions, and empty states

---

## Technical Implementation

### State Management
- React hooks (useState, useEffect, useRef) for local component state
- Props drilling for alert count synchronization
- Modal/dialog state properly managed with open/close handlers

### Animation & Transitions
- Tailwind transition classes for smooth animations
- Framer Motion ready for advanced animations
- CSS animations for typing indicator

### Component Reusability
- RecommendationModal component reused across app
- AlertCard, MetricWidget, AgentStatusCard all reusable
- Consistent UI patterns with shadcn/ui components

---

## Future Enhancement Opportunities

1. **Persistent Preferences**: Save collapsed states to localStorage
2. **Drag-and-Drop Calendar**: Fully functional event rescheduling
3. **Real-time Updates**: WebSocket integration for live alerts
4. **Advanced Filters**: Save and reuse filter presets
5. **Bulk Actions**: Select multiple alerts to dismiss at once
6. **Keyboard Shortcuts**: Power user shortcuts (Cmd+K for search, etc.)
7. **Dark Mode**: Toggle between light/dark themes
8. **Offline Support**: Progressive Web App with offline capabilities

---

## Conclusion

These UX improvements transform Growgent from a functional prototype into a polished, user-friendly agricultural management platform. Every interaction has been considered, every action provides feedback, and users maintain full control over their workspace and information density.

---
--- frontend/DEBUGGING_GUIDE.md ---

# Frontend Debugging Guide

## ✅ Fixed Issues

### 1. **Port Configuration**
- ✅ Updated `vite.config.ts` to use port **3001**
- ✅ Backend CORS already allows `http://localhost:3001`
- ✅ Server configured to not auto-open browser

### 2. **Error Handling**
- ✅ Added comprehensive error handling in `main.tsx`
- ✅ Added console logging for debugging
- ✅ Added user-friendly error messages
- ✅ Error boundaries in place

### 3. **HTML Structure**
- ✅ Fixed `index.html` formatting
- ✅ Added loading indicator for empty root
- ✅ Added proper meta tags and styling

## 🔍 Debugging Steps

### If you see a blank screen:

1. **Open Browser Console (F12)**
   - Look for console logs:
     - `🚀 Growgent Frontend: Initializing application...`
     - `✅ Root element found, creating React root...`
     - `✅ Rendering App component...`
     - `✅ Application rendered successfully!`
     - `📱 App component rendering...`

2. **Check for Errors**
   - Red errors in console = JavaScript/TypeScript errors
   - Network errors = API connection issues
   - CORS errors = Backend not allowing frontend origin

3. **Verify Server is Running**
   ```powershell
   # Check if port 3001 is listening
   netstat -ano | findstr :3001
   
   # Test server response
   Invoke-WebRequest -Uri http://localhost:3001 -UseBasicParsing
   ```

4. **Check Network Tab**
   - Open DevTools → Network tab
   - Refresh page
   - Look for failed requests (red)
   - Check if `main.tsx` loads successfully

5. **Verify Backend Connection**
   - Backend should be running on `http://localhost:8000`
   - Check CORS allows `http://localhost:3001`
   - Test backend health: `curl http://localhost:8000/health`

## 🚀 Starting the Server

```powershell
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev
```

The server will start on `http://localhost:3001`

## 📋 Expected Console Output

When everything works correctly, you should see:

```
🚀 Growgent Frontend: Initializing application...
✅ Root element found, creating React root...
✅ Rendering App component...
✅ Application rendered successfully!
📱 App component rendering...
```

## 🐛 Common Issues

### Issue: Blank Screen with No Console Logs
**Solution**: Check if `main.tsx` is loading. Open Network tab and verify `/main.tsx` returns 200.

### Issue: CORS Errors
**Solution**: Ensure backend `ALLOWED_ORIGINS` includes `http://localhost:3001`

### Issue: Module Not Found Errors
**Solution**: Run `npm install` to ensure all dependencies are installed.

### Issue: React Component Errors
**Solution**: Check browser console for specific component errors. Error boundaries should catch these.

## 🔧 Quick Fixes

1. **Clear Browser Cache**: Hard refresh (Ctrl+Shift+R)
2. **Restart Dev Server**: Stop and restart `npm run dev`
3. **Reinstall Dependencies**: `rm -rf node_modules && npm install`
4. **Check TypeScript**: Run `npm run type-check`

## 📞 Next Steps

If you still see a blank screen after checking all above:
1. Share the browser console errors
2. Share the Network tab showing failed requests
3. Verify backend is running and accessible

---
--- frontend/FRONTEND_BACKEND_CONNECTION.md ---

# Frontend-Backend Connection Status

## ✅ Fixed Issues

1. **Missing Dependency**: Installed `@tanstack/react-query` package
2. **Sonner Component**: Fixed import to work with Vite (removed Next.js-specific code)
3. **Frontend Server**: Now running successfully on `http://localhost:3000`

## 🔧 Current Status

### Frontend
- ✅ Running on `http://localhost:3000`
- ✅ All dependencies installed
- ✅ React Query configured
- ✅ API client ready to connect

### Backend
- ⚠️ **Needs to be started manually**

## 🚀 Starting the Backend

Open a **new terminal** and run:

```powershell
cd Backend
.\venv\Scripts\activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## 🧪 Testing the Connection

### 1. Test Backend Health
```powershell
curl http://localhost:8000/health
```
Expected: `{"status":"healthy"}`

### 2. Test API Endpoints
```powershell
# Fields endpoint
curl http://localhost:8000/api/fields

# Critical alerts
curl http://localhost:8000/api/alerts/critical?limit=5

# Recommendations
curl http://localhost:8000/api/agents/irrigation/recommendations?page=1&page_size=5
```

### 3. Test Frontend-Backend Connection

1. Open browser to `http://localhost:3000`
2. Open Developer Console (F12)
3. Go to Network tab
4. Check for API requests:
   - Should see requests to `/api/alerts/critical`
   - Should see requests to `/api/agents/irrigation/recommendations`
   - Should see requests to `/api/fields`
5. Check Console tab for any errors

## 📋 API Endpoints Configured

The frontend is configured to call these endpoints:

| Endpoint | Purpose | Component |
|----------|---------|-----------|
| `/api/alerts/critical` | Get critical alerts | Dashboard |
| `/api/alerts` | List all alerts | Alerts page |
| `/api/alerts/{id}/acknowledge` | Acknowledge alert | Alerts page |
| `/api/agents/irrigation/recommendations` | Get recommendations | Dashboard, Schedule |
| `/api/recommendations/{id}/accept` | Accept recommendation | RecommendationModal |
| `/api/fields` | List fields | Dashboard, Schedule |
| `/api/fields/{id}` | Get field details | FieldsMap |
| `/api/metrics/water` | Water metrics | WaterMetrics |
| `/api/metrics/fire-risk` | Fire risk metrics | FireRiskMetrics |

## 🔍 Troubleshooting

### Frontend shows "Failed to load dashboard data"
- **Check**: Is backend running on port 8000?
- **Fix**: Start backend server (see above)

### CORS Errors in Browser Console
- **Check**: Backend CORS configuration in `Backend/app/main.py`
- **Fix**: Ensure `localhost:3000` is in `ALLOWED_ORIGINS`

### API Returns 404
- **Check**: Endpoint path matches backend routes
- **Fix**: Verify endpoint in `Backend/app/api/` files

### API Returns 500
- **Check**: Database is running and initialized
- **Fix**: Run `python Backend/scripts/init_database.py`

### No Data Displayed
- **Check**: Database has data (fields, alerts, recommendations)
- **Fix**: Add test data or check database connection

## ✅ Success Indicators

When everything is working:
- ✅ Frontend loads without errors
- ✅ Dashboard shows data (or "No data" message)
- ✅ Network tab shows successful API calls (200 status)
- ✅ No CORS errors in console
- ✅ React Query DevTools shows queries (if installed)

## 📝 Next Steps

1. Start backend server
2. Verify backend health endpoint
3. Open frontend in browser
4. Check browser console for errors
5. Verify API calls in Network tab
6. Test user interactions (acknowledge alerts, accept recommendations)
