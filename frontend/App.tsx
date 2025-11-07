import { useState } from "react";
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

export default function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [alertCount, setAlertCount] = useState(3);

  const handleDismissAlert = () => {
    setAlertCount(Math.max(0, alertCount - 1));
  };

  const renderPage = () => {
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
        onNavigate={setCurrentPage}
        alertCount={alertCount}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <AppHeader
          farmName="Sunnydale Farm"
          notificationCount={alertCount}
          onNotificationClick={() => setCurrentPage("alerts")}
          onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)}
          sidebarCollapsed={sidebarCollapsed}
        />
        
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-7xl mx-auto">
            {renderPage()}
          </div>
        </main>
      </div>
      
      <Toaster />
    </div>
  );
}
