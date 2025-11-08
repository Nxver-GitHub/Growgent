// src/App.tsx
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
import type { Page } from "./lib/types";

function AppContent(): JSX.Element {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // same API-driven alert count you added
  const { data: criticalAlertsData, error: alertsError } = useCriticalAlerts({
    limit: 100,
  });

  const alertCount = useMemo(() => {
    if (alertsError) return 0;
    return (
      criticalAlertsData?.count || criticalAlertsData?.alerts?.length || 0
    );
  }, [criticalAlertsData, alertsError]);

  const handleDismissAlert = useCallback(() => {
    // server-driven now, so nothing to do
  }, []);

  const renderPage = () => {
    switch (currentPage) {
      case "dashboard":
        return (
          <Dashboard
            onNavigate={setCurrentPage}
            onDismissAlert={handleDismissAlert}
          />
        );
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
        return (
          <Dashboard
            onNavigate={setCurrentPage}
            onDismissAlert={handleDismissAlert}
          />
        );
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

        <main className="flex-1 overflow-y-auto p-8 bg-slate-50">
          <div className="max-w-7xl mx-auto w-full">{renderPage()}</div>
        </main>
      </div>

      {/* mobile bottom bar */}
      <MobileNav
        currentPage={currentPage}
        onNavigate={(page: Page) => setCurrentPage(page)}
        alertCount={alertCount}
      />

      <Toaster />
    </div>
  );
}

export default function App(): JSX.Element {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AppContent />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
