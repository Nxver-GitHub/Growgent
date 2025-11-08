import {
  LayoutDashboard,
  Map,
  Calendar,
  Flame,
  Droplet,
  Bell,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import type { Page } from "../lib/types";

interface AppSidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  alertCount?: number;
  collapsed?: boolean;
  onToggleCollapse: () => void;
}

export function AppSidebar({
  currentPage,
  onNavigate,
  alertCount = 0,
  collapsed = false,
  onToggleCollapse,
}: AppSidebarProps): JSX.Element {
  const items: Array<{
    id: Page;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: number;
  }> = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "fields", label: "Fields", icon: Map },
    { id: "schedule", label: "Irrigation Schedule", icon: Calendar },
    { id: "fire-risk", label: "Fire Risk", icon: Flame },
    { id: "metrics", label: "Water Metrics", icon: Droplet },
    { id: "alerts", label: "Alerts", icon: Bell, badge: alertCount },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={`hidden md:flex h-screen bg-white border-r border-slate-200 flex-col shrink-0 transition-all duration-300 ease-in-out z-[110] ${
        collapsed ? "w-16" : "w-64"
      }`}
      data-sidebar="main"
    >
      {/* header with logo */}
      <div className="border-b border-slate-200 p-4 relative">
      {/* logo pinned to same x-position as sidebar icons */}
      <div className="absolute left-6 top-1/2 -translate-y-1/2">
        <div className="w-8 h-8 aspect-square rounded-xl bg-emerald-500 flex items-center justify-center">
          <Droplet className="h-6 w-6 text-white" fill="white" />
        </div>
      </div>

      {/* centered title */}
      {!collapsed && (
        <div className="flex flex-col items-center justify-center text-center">
          <p className="text-lg font-semibold text-emerald-700leading-tight">
            Growgent
          </p>
          <p className="text-sm text-slate-500 leading-tight">
          </p>
        </div>
      )}
    </div>

      {/* navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2">
        {items.map((item) => {
          const Icon = item.icon;
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center mb-1 ${
                collapsed ? "justify-center px-2" : "px-3"
              } py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-emerald-50 text-emerald-700"
                  : "text-slate-700 hover:bg-slate-50"
              }`}
            >
              <div className="relative flex-shrink-0">
                <Icon
                  className={`h-5 w-5 ${
                    active ? "text-emerald-600" : "text-slate-500"
                  } ${!collapsed ? "mr-3" : ""}`}
                />
                {collapsed && item.id === "alerts" && alertCount > 0 && (
                  <span className="absolute -top-1 -right-1 inline-flex min-w-[1.25rem] h-5 items-center justify-center rounded-full bg-red-500 text-white text-[10px] px-1 border-2 border-white">
                    {alertCount > 9 ? "9+" : alertCount}
                  </span>
                )}
              </div>
              {!collapsed && (
                <>
                  <span className="flex-1 text-left whitespace-nowrap overflow-hidden text-ellipsis">
                    {item.label}
                  </span>
                  {item.id === "alerts" && alertCount > 0 && (
                    <span className="text-slate-500 text-xs ml-2 whitespace-nowrap flex-shrink-0">
                      {alertCount}
                    </span>
                  )}
                </>
              )}
            </button>
          );
        })}
      </nav>

        {/* collapse button */}
        <div className="border-t border-slate-200 p-3 flex-shrink-0">
          <button
            type="button"
            onClick={onToggleCollapse}
            className={`w-full flex items-center ${
              collapsed ? "justify-center px-2" : "px-3"
            } py-2 rounded-md text-slate-500 hover:bg-slate-50 transition-colors text-sm`}
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4 mr-2" />
                <span>Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>
  );
}
