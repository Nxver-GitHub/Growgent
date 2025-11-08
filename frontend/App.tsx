/**
 * Main application component for Growgent.
 *
 * Manages the overall application layout, navigation state, and page routing.
 * Provides the main container for all application pages and components.
 *
 * @component
 * @returns {JSX.Element} The main application layout
 */
import { useState, useCallback, useMemo } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/api";
import { AppSidebar } from "./components/AppSidebar";
import { AppHeader } from "./components/AppHeader";
import { Dashboard } from "./components/Dashboard";
import { IrrigationSchedule } from "./components/IrrigationSchedule";
import { FieldsMap } from "./components/FieldsMap";
import { WaterMetrics } from "./components/WaterMetrics";
import { Alerts } from "./components/Alerts";
import { Chat } from "./components/Chat";
import { Settings } from "./components/Settings";
import { MobileNav } from "./components/layout/MobileNav";
import { Toaster } from "./components/ui/sonner";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { useCriticalAlerts } from "./lib/hooks/useAlerts";

type Page =
  | "dashboard"
  | "schedule"
  | "fields"
  | "fire-risk"
  | "metrics"
  | "alerts"
  | "chat"
  | "settings";

/**
 * Inner app component that uses React Query hooks.
 * Must be inside QueryClientProvider.
 */
function AppContent(): JSX.Element {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  
  // Fetch alert count from API (with error handling)
  const { data: criticalAlertsData, error: alertsError } = useCriticalAlerts({ limit: 100 });
  
  // Memoize alert count to prevent unnecessary re-renders
  const alertCount = useMemo(() => {
    if (alertsError) {
      // Only log error once, not on every render
      if (process.env.NODE_ENV === "development") {
        console.warn("⚠️ Failed to fetch alerts count:", alertsError);
      }
      return 0;
    }
    return criticalAlertsData?.count || criticalAlertsData?.alerts?.length || 0;
  }, [criticalAlertsData, alertsError]);

  /**
   * Handles dismissing an alert (alert count is now dynamic from API).
   */
  const handleDismissAlert = useCallback((): void => {
    // Alert count is now fetched from API, no need to manage state
  }, []);

  /**
   * Renders the appropriate page component based on current navigation state.
   *
   * @returns {JSX.Element} The page component to render
   */
  const renderPage = (): JSX.Element => {
    switch (currentPage) {
      case "dashboard":
        return <Dashboard onNavigate={setCurrentPage} onDismissAlert={handleDismissAlert} />;
      case "schedule":
        return <IrrigationSchedule />;
      case "fields":
      case "fire-risk":
        return <FieldsMap />;
      case "metrics":
        return <WaterMetrics />;
      case "alerts":
        return <Alerts onDismissAlert={handleDismissAlert} />;
      case "chat":
        return <Chat />;
      case "settings":
        return <Settings />;
      default:
        return <Dashboard onNavigate={setCurrentPage} onDismissAlert={handleDismissAlert} />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <AppSidebar
        currentPage={currentPage}
        onNavigate={(page: Page) => setCurrentPage(page)}
        alertCount={alertCount}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
      />

      <div className="flex-1 flex flex-col overflow-hidden min-w-0">
        <AppHeader
          farmName="Sunnydale Farm"
          notificationCount={alertCount}
          onNotificationClick={() => setCurrentPage("alerts")}
          onToggleSidebar={() => setSidebarCollapsed((prev) => !prev)}
          sidebarCollapsed={sidebarCollapsed}
        />

          <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 pb-20 md:pb-8 relative z-0 bg-slate-50">
            <ErrorBoundary>
              <div className="max-w-7xl mx-auto w-full">{renderPage()}</div>
            </ErrorBoundary>
          </main>
      </div>

      <MobileNav
        currentPage={currentPage}
        onNavigate={(page: Page) => setCurrentPage(page)}
        alertCount={alertCount}
      />

      <Toaster />
    </div>
  );
}

/**
 * Main App component with providers.
 */
export default function App(): JSX.Element {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
