# Growgent Frontend MVP Gap Analysis & Action Plan

**Date:** Current  
**Status:** In Progress  
**Reference:** [Figma Design](https://www.figma.com/make/3QozQgwbyWOM5ycZNpGIKF/Growgent-Frontend-UI-UX-Design?node-id=0-4&t=4TPKcD2qo6s9hBEG-1)

---

## 🎯 Executive Summary

The frontend is **~70% complete** for MVP. Core components exist but need enhancements to match the Figma design and full functionality requirements. The main gaps are:

1. **Performance Issues:** Excessive re-rendering causing console noise
2. **Map Integration:** FieldsMap lacks actual Mapbox GL JS implementation
3. **Chat Integration:** Missing Agentforce backend connection
4. **Data Visualization:** WaterMetrics needs Recharts integration
5. **Calendar Features:** Drag-to-reschedule not implemented
6. **Design Polish:** Spacing, typography, and color alignment with Figma
7. **Mobile UX:** Additional responsive refinements needed

---

## 📊 Current Component Status

| Component | Status | Completion | Priority |
|-----------|--------|------------|----------|
| **Dashboard** | ✅ Functional | 85% | High |
| **AppSidebar** | ✅ Functional | 90% | Medium |
| **AppHeader** | ✅ Functional | 90% | Medium |
| **Alerts** | ✅ Functional | 80% | High |
| **IrrigationSchedule** | ⚠️ Partial | 60% | High |
| **FieldsMap** | ⚠️ Placeholder | 40% | High |
| **WaterMetrics** | ⚠️ Partial | 50% | Medium |
| **Chat** | ⚠️ UI Only | 40% | Medium |
| **Settings** | ✅ Basic | 70% | Low |
| **MobileNav** | ✅ Functional | 85% | Medium |

---

## 🔴 Critical Issues (Fix First)

### 1. Excessive Re-rendering
**Problem:** `AppContent` renders multiple times per second, causing:
- Console noise
- Potential performance degradation
- Unnecessary API calls

**Root Cause:** React Query hooks triggering re-renders on error states

**Solution:**
```typescript
// In App.tsx - Add memoization and error boundary handling
const alertCount = useMemo(() => {
  if (alertsError) return 0;
  return criticalAlertsData?.count || criticalAlertsData?.alerts?.length || 0;
}, [criticalAlertsData, alertsError]);
```

**Files to Fix:**
- `frontend/App.tsx` (lines 48-53)
- `frontend/lib/hooks/useAlerts.ts` (add error state handling)

---

### 2. Backend Connection Handling
**Problem:** Console shows repeated "Failed to fetch" errors when backend is offline

**Solution:** Already implemented offline detection, but need to:
- Suppress console warnings in production
- Add retry logic with exponential backoff when backend comes online
- Show connection status indicator in header

**Files to Fix:**
- `frontend/lib/api.ts` (add connection status tracking)
- `frontend/components/AppHeader.tsx` (add status indicator)

---

## 🟡 High Priority Enhancements

### 3. FieldsMap - Mapbox Integration
**Current State:** Placeholder UI with layer toggles, no actual map

**Required:**
- [ ] Install `mapbox-gl` and `@react-map-gl`
- [ ] Create Mapbox GL JS map component
- [ ] Add field boundary polygons (GeoJSON from API)
- [ ] Add sensor markers with popups
- [ ] Implement NDVI heatmap overlay
- [ ] Add fire risk zone layers (red/orange/yellow)
- [ ] Add PSPS shutoff area overlays (purple)
- [ ] Add irrigation recommendation pins
- [ ] Implement field selection (click polygon → update sidebar)
- [ ] Add map controls (zoom, recenter, basemap toggle)
- [ ] Mobile: Full-height map with bottom sheet sidebar

**Files to Create/Modify:**
- `frontend/components/FieldsMap.tsx` (complete rewrite)
- `frontend/lib/hooks/useMapData.ts` (new)
- `frontend/lib/utils/mapbox.ts` (new)
- `frontend/package.json` (add dependencies)

**Dependencies:**
```json
{
  "mapbox-gl": "^3.0.0",
  "@react-map-gl/core": "^7.0.0",
  "@react-map-gl/markers": "^7.0.0"
}
```

---

### 4. IrrigationSchedule - Drag-to-Reschedule
**Current State:** Calendar displays events, but no drag functionality

**Required:**
- [ ] Install `react-dnd` or use native HTML5 drag-drop
- [ ] Make calendar events draggable
- [ ] Add drop zones for each day
- [ ] Show visual feedback during drag (ghost element)
- [ ] Validate drops (prevent dropping on PSPS windows)
- [ ] Call API to update recommendation on drop
- [ ] Show optimistic UI updates
- [ ] Handle conflicts (show error toast)
- [ ] Add confirmation dialog for critical changes

**Files to Modify:**
- `frontend/components/IrrigationSchedule.tsx`
- `frontend/lib/hooks/useRecommendations.ts` (add update mutation)

**Dependencies:**
```json
{
  "react-dnd": "^16.0.0",
  "react-dnd-html5-backend": "^16.0.0"
}
```

---

### 5. Chat - Agentforce Integration
**Current State:** UI exists, but no backend connection

**Required:**
- [ ] Connect to `/api/agents/chat` endpoint
- [ ] Implement message sending with loading states
- [ ] Handle streaming responses (if backend supports)
- [ ] Add quick commands (`/weather`, `/irrigation`, `/fire-risk`, `/help`)
- [ ] Show action buttons in bot responses ([Accept], [View Schedule], [Details])
- [ ] Add message persistence (localStorage or sessionStorage)
- [ ] Handle errors gracefully (show "Agent offline" message)
- [ ] Add typing indicators
- [ ] Implement message history pagination

**Files to Modify:**
- `frontend/components/Chat.tsx`
- `frontend/lib/hooks/useChat.ts` (enhance with API calls)
- `frontend/lib/api.ts` (add chat API functions)

---

### 6. WaterMetrics - Charts & Analytics
**Current State:** KPI cards exist, but no charts

**Required:**
- [ ] Install `recharts`
- [ ] Create water use over time chart (area chart: recommended vs. actual)
- [ ] Create fire risk trajectory chart (line chart)
- [ ] Create crop health (NDVI) trend chart
- [ ] Create drought stress bar chart by week
- [ ] Create agent performance table
- [ ] Add date range selector (Last 30 days, Q3, Year, Custom)
- [ ] Implement PDF export (jsPDF or html2canvas)
- [ ] Implement CSV export
- [ ] Add email report functionality (optional)

**Files to Modify:**
- `frontend/components/WaterMetrics.tsx`
- `frontend/lib/hooks/useMetrics.ts` (enhance with date range)
- `frontend/components/charts/` (new directory for chart components)

**Dependencies:**
```json
{
  "recharts": "^2.10.0",
  "jspdf": "^2.5.0",
  "html2canvas": "^1.4.0"
}
```

---

## 🟢 Medium Priority - Design Polish

### 7. Design System Alignment
**Current State:** Colors and spacing are close, but need refinement

**Required:**
- [ ] Verify exact colors from Figma (Emerald #10B981, Sky #0EA5E9, etc.)
- [ ] Update Tailwind config with exact color values
- [ ] Standardize spacing (8px units: 8, 16, 24, 32, 40, 48)
- [ ] Standardize border radius (8px default, 12px cards, 16px large)
- [ ] Standardize shadows (subtle, medium, large)
- [ ] Update typography (Inter for headings/body, JetBrains Mono for data)
- [ ] Add font loading optimization
- [ ] Verify all components match Figma spacing

**Files to Modify:**
- `frontend/tailwind.config.js`
- `frontend/index.css` (font imports)
- All component files (spacing/color updates)

---

### 8. Dashboard Hero Section
**Current State:** Hero exists but may not match Figma exactly

**Required:**
- [ ] Verify hero text: "Your Farm is Ready for Climate Action"
- [ ] Ensure 3 CTAs are present and styled correctly
- [ ] Match gradient colors exactly
- [ ] Verify spacing and typography
- [ ] Add decorative elements if in Figma

**Files to Modify:**
- `frontend/components/Dashboard.tsx` (hero section)

---

### 9. Agent Status Cards
**Current State:** Cards exist and display data

**Required:**
- [ ] Verify all 4 cards match Figma design exactly
- [ ] Ensure status indicators (active/warning/error) are correct
- [ ] Verify metric display format
- [ ] Check icon usage and sizing
- [ ] Verify hover states and interactions

**Files to Modify:**
- `frontend/components/AgentStatusCard.tsx`
- `frontend/components/Dashboard.tsx` (card usage)

---

## 🔵 Low Priority - Nice to Have

### 10. Settings Page Enhancement
**Current State:** Basic settings page exists

**Required:**
- [ ] Add Profile settings
- [ ] Add Farm Settings
- [ ] Add Notifications preferences
- [ ] Add Data Privacy settings
- [ ] Add export data functionality

---

### 11. Accessibility Improvements
**Required:**
- [ ] Add ARIA labels to all interactive elements
- [ ] Ensure keyboard navigation works everywhere
- [ ] Test with screen reader (NVDA/JAWS)
- [ ] Verify color contrast ratios (WCAG 2.1 AA)
- [ ] Add focus indicators
- [ ] Add skip links

---

### 12. Performance Optimization
**Required:**
- [ ] Run Lighthouse audit (target: >80 performance, >95 accessibility)
- [ ] Implement code splitting for routes
- [ ] Lazy load images
- [ ] Optimize bundle size
- [ ] Add service worker for offline support (optional)

---

## 📋 Implementation Checklist

### Phase 1: Critical Fixes (Do First)
- [ ] Fix excessive re-rendering in App.tsx
- [ ] Suppress console warnings in production
- [ ] Add connection status indicator

### Phase 2: High Priority Features
- [ ] Implement Mapbox in FieldsMap
- [ ] Add drag-to-reschedule in IrrigationSchedule
- [ ] Connect Chat to Agentforce backend
- [ ] Add charts to WaterMetrics

### Phase 3: Design Polish
- [ ] Align design system with Figma
- [ ] Polish Dashboard hero section
- [ ] Verify Agent Status Cards match design
- [ ] Mobile responsiveness testing and fixes

### Phase 4: Testing & Optimization
- [ ] Component tests (60%+ coverage)
- [ ] E2E tests (Playwright)
- [ ] Lighthouse audit
- [ ] Accessibility audit

---

## 🛠️ Technical Debt

1. **Framework Mismatch:** Prompt specifies Next.js 14+, but project uses Vite + React
   - **Status:** User confirmed to ignore migration for now
   - **Action:** Continue with Vite, but note for future

2. **Type Safety:** Some components use `any` types
   - **Action:** Add strict typing throughout

3. **Error Handling:** Some API calls lack comprehensive error handling
   - **Action:** Add error boundaries and user-friendly error messages

4. **Loading States:** Some components lack skeleton loaders
   - **Action:** Add loading states to all data-fetching components

---

## 📝 Notes

- **Backend Status:** Backend is not currently running (connection refused errors)
- **Figma Access:** Design reference available at provided Figma link
- **Testing:** Need to test with backend running to verify full functionality
- **Mobile:** Test on actual devices (375px, 768px, 1024px, 1920px)

---

## 🎯 Success Criteria

The frontend will be MVP-ready when:
- ✅ All pages render without errors
- ✅ All components match Figma design
- ✅ All interactive features work (drag-drop, chat, map)
- ✅ Mobile responsive at all breakpoints
- ✅ Accessibility score >95
- ✅ Performance score >80
- ✅ Component tests pass (60%+ coverage)
- ✅ Zero TypeScript errors

---

**Next Steps:** Start with Phase 1 (Critical Fixes), then proceed to Phase 2 (High Priority Features).

