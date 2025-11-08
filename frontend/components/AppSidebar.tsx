/**
 * AppSidebar component displays the main navigation sidebar.
 *
 * Provides navigation between different pages and shows alert counts.
 * Supports collapsed/expanded states.
 *
 * @component
 * @param {AppSidebarProps} props - Component props
 * @returns {JSX.Element} The application sidebar
 */
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
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip";
import type { Page } from "../lib/types";

interface AppSidebarProps {
  /** Current active page */
  currentPage: Page;
  /** Callback function for page navigation */
  onNavigate: (page: Page) => void;
  /** Optional count of active alerts */
  alertCount?: number;
  /** Whether the sidebar is collapsed */
  collapsed?: boolean;
  /** Callback to toggle sidebar collapse state */
  onToggleCollapse: () => void;
}

export function AppSidebar({
  currentPage,
  onNavigate,
  alertCount = 0,
  collapsed = false,
  onToggleCollapse,
}: AppSidebarProps): JSX.Element {
  const menuItems = [
    { id: "dashboard", icon: LayoutDashboard, label: "Dashboard" },
    { id: "fields", icon: Map, label: "Fields" },
    { id: "schedule", icon: Calendar, label: "Irrigation Schedule" },
    { id: "fire-risk", icon: Flame, label: "Fire Risk" },
    { id: "metrics", icon: Droplet, label: "Water Metrics" },
    { id: "alerts", icon: Bell, label: "Alerts", badge: alertCount },
    { id: "chat", icon: MessageSquare, label: "Chat with Agents" },
    { id: "settings", icon: Settings, label: "Settings" },
  ];

  return (
    <TooltipProvider>
      <div
        className={`hidden md:flex bg-white border-r border-slate-200 h-screen flex-col transition-all duration-300 flex-shrink-0 ${
          collapsed ? "w-20" : "w-64"
        }`}
      >
        <div className="p-6 border-b border-slate-200 bg-gradient-to-r from-emerald-50 to-sky-50">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-sky-500 rounded-xl flex items-center justify-center shrink-0 shadow-md">
              <Droplet className="h-6 w-6 text-white" />
            </div>
            {!collapsed && <h2 className="text-emerald-700 font-bold text-xl">Growgent</h2>}
          </div>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;

              const button = (
                <Button
                  variant={isActive ? "secondary" : "ghost"}
                  className={`w-full ${collapsed ? "justify-center px-2" : "justify-start"} transition-all duration-200 ${
                    isActive 
                      ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-md font-semibold" 
                      : "text-slate-700 hover:bg-emerald-50 hover:text-emerald-700"
                  }`}
                  onClick={() => onNavigate(item.id)}
                >
                  <Icon className={`h-5 w-5 ${collapsed ? "" : "mr-3"} shrink-0`} />
                  {!collapsed && <span className="flex-1 text-left">{item.label}</span>}
                  {!collapsed && item.badge && item.badge > 0 && (
                    <Badge variant="destructive" className="ml-auto rounded-full">
                      {item.badge}
                    </Badge>
                  )}
                  {collapsed && item.badge && item.badge > 0 && (
                    <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white">
                      {item.badge}
                    </div>
                  )}
                </Button>
              );

              return (
                <li key={item.id} className="relative">
                  {collapsed ? (
                    <Tooltip>
                      <TooltipTrigger asChild>{button}</TooltipTrigger>
                      <TooltipContent side="right">
                        <p>{item.label}</p>
                      </TooltipContent>
                    </Tooltip>
                  ) : (
                    button
                  )}
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-slate-200">
          <Button
            variant="ghost"
            size="sm"
            className={`w-full ${collapsed ? "justify-center px-2" : "justify-start"} text-slate-600`}
            onClick={onToggleCollapse}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <>
                <ChevronLeft className="h-4 w-4 mr-2" />
                Collapse
              </>
            )}
          </Button>
        </div>
      </div>
    </TooltipProvider>
  );
}
