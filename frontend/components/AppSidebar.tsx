import {
  LayoutDashboard,
  Map,
  Calendar,
  Flame,
  Droplet,
  Bell,
  MessageSquare,
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
    { id: "chat", label: "Chat with Agents", icon: MessageSquare },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside
      className={`hidden md:flex h-screen bg-white border-r border-slate-200 flex-col shrink-0 transition-all duration-200 z-50 ${
        collapsed ? "w-16" : "w-64"
      }`}
    >

      {/* header with left logo and centered text */}
      <div className="h-20 flex items-center justify-center border-b border-slate-200 px-4 pb-4 relative">
        {/* logo fixed to left */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center">
          <Droplet className="h-4 w-4 text-white" />
        </div>

        {/* text centered horizontally */}
        {!collapsed && (
          <div className="text-center">
            <p className="text-sm font-semibold text-emerald-700">Growgent</p>
            <p className="text-xs text-slate-400">Climate-smart farming</p>
          </div>
        )}
      </div>

      {/* navigation */}
      <ul className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {items.map((item) => {
          const Icon = item.icon;
          const active = currentPage === item.id;
          return (
            <li key={item.id} className="relative">
              <button
                type="button"
                onClick={() => onNavigate(item.id)}
                className={`flex w-full items-center rounded-md ${
                  collapsed ? "justify-center" : "justify-start"
                } ${collapsed ? "px-0" : "px-3"} py-2 text-sm transition-colors ${
                  active
                    ? "bg-emerald-50 text-emerald-700"
                    : "text-slate-700 hover:bg-slate-50"
                }`}
              >
                <Icon
                  className={`h-5 w-5 flex-shrink-0 ${
                    !collapsed ? "mr-3" : ""
                  } ${active ? "text-emerald-600" : "text-slate-500"}`}
                />
                {!collapsed && <span className="flex-1">{item.label}</span>}

                {!collapsed && item.badge && item.badge > 0 && (
                  <span className="ml-auto inline-flex min-w-[1.25rem] h-5 items-center justify-center rounded-full bg-red-500 text-white text-[10px] px-1.5">
                    {item.badge}
                  </span>
                )}
                {collapsed && item.badge && item.badge > 0 && (
                  <span className="absolute -top-1 -right-1 inline-flex w-5 h-5 items-center justify-center rounded-full bg-red-500 text-white text-[10px]">
                    {item.badge > 9 ? "9+" : item.badge}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>

      {/* collapse button */}
      <div className="border-t border-slate-200 p-3">
        <button
          type="button"
          onClick={onToggleCollapse}
          className={`flex w-full items-center rounded-md text-slate-500 hover:bg-slate-50 transition ${
            collapsed ? "justify-center py-2" : "justify-start gap-2 px-2 py-2"
          }`}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span className="text-sm">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  );
}
