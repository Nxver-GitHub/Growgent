import {
  LayoutDashboard,
  Map,
  Calendar,
  Flame,
  Droplet,
  Bell,
  MessageSquare,
  Settings,
} from "lucide-react";
import type { Page } from "../lib/types";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";

interface AppNavbarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  alertCount?: number;
}

export function AppNavbar({
  currentPage,
  onNavigate,
  alertCount = 0,
}: AppNavbarProps): JSX.Element {
  const items: Array<{
    id: Page;
    label: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: number;
  }> = [
    { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { id: "fields", label: "Fields", icon: Map },
    { id: "schedule", label: "Schedule", icon: Calendar },
    { id: "fire-risk", label: "Fire Risk", icon: Flame },
    { id: "metrics", label: "Water Metrics", icon: Droplet },
    { id: "alerts", label: "Alerts", icon: Bell, badge: alertCount },
    { id: "chat", label: "Chat", icon: MessageSquare },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <nav className="w-full bg-white border-b-2 border-slate-200 shadow-sm z-[110] sticky top-0">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center">
              <Droplet className="h-4 w-4 text-white" />
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-semibold text-emerald-700">Growgent</p>
              <p className="text-xs text-slate-400">Climate-smart farming</p>
            </div>
          </div>

          {/* Navigation Items */}
          <div className="flex-1 flex items-center justify-center gap-1 overflow-x-auto">
            {items.map((item) => {
              const Icon = item.icon;
              const active = currentPage === item.id;
              return (
                <Button
                  key={item.id}
                  type="button"
                  variant="ghost"
                  onClick={() => onNavigate(item.id)}
                  className={`flex flex-col items-center gap-1 px-3 py-2 h-auto min-w-[70px] transition-colors ${
                    active
                      ? "bg-emerald-50 text-emerald-700"
                      : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <div className="relative">
                    <Icon
                      className={`h-5 w-5 ${
                        active ? "text-emerald-600" : "text-slate-500"
                      }`}
                    />
                    {item.id === "alerts" && alertCount > 0 && (
                      <Badge
                        variant="destructive"
                        className="absolute -top-2 -right-2 h-4 w-4 flex items-center justify-center p-0 rounded-full text-[10px] border-2 border-white"
                      >
                        {alertCount > 9 ? "9+" : alertCount}
                      </Badge>
                    )}
                  </div>
                  <span className="text-xs whitespace-nowrap">{item.label}</span>
                </Button>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}

