/**
 * Main application component for Growgent.
 *
 * Manages the overall application layout, navigation state, and page routing.
 * Provides the main container for all application pages and components.
 *
 * @component
 * @returns {JSX.Element} The main application layout
 */
import { useState, useCallback } from "react";
import { AppSidebar } from "./components/AppSidebar";
import { AppHeader } from "./components/AppHeader";
import { Dashboard } from "./components/Dashboard";
import { IrrigationSchedule } from "./components/IrrigationSchedule";
import { FieldsMap } from "./components/FieldsMap";
import { WaterMetrics } from "./components/WaterMetrics";
import { Alerts } from "./components/Alerts";
import { Chat } from "./components/Chat";
import { Settings } from "./components/Settings";
import { Toaster } from "./components/ui/sonner";

type Page =
  | "dashboard"
  | "schedule"
  | "fields"
  | "fire-risk"
  | "metrics"
  | "alerts"
  | "chat"
  | "settings";

export default function App(): JSX.Element {
  const [currentPage, setCurrentPage] = useState<Page>("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [alertCount, setAlertCount] = useState<number>(3);

  /**
   * Handles dismissing an alert and decrements the alert count.
   */
  const handleDismissAlert = useCallback((): void => {
    setAlertCount((prev) => Math.max(0, prev - 1));
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
    <div className="flex h-screen bg-slate-50">
      <AppSidebar
        currentPage={currentPage}
        onNavigate={(page: Page) => setCurrentPage(page)}
        alertCount={alertCount}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <AppHeader
          farmName="Sunnydale Farm"
          notificationCount={alertCount}
          onNotificationClick={() => setCurrentPage("alerts")}
          onToggleSidebar={() => setSidebarCollapsed((prev) => !prev)}
          sidebarCollapsed={sidebarCollapsed}
        />

        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">{renderPage()}</div>
        </main>
      </div>

      <Toaster />
    </div>
  );
}
