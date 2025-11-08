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
