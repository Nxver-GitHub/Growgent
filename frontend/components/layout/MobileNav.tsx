/**
 * MobileNav component provides bottom navigation for mobile devices.
 *
 * Displays 5 main navigation tabs at the bottom of the screen on mobile.
 * Hidden on desktop (md and above).
 *
 * @component
 * @param {MobileNavProps} props - Component props
 * @returns {JSX.Element} The mobile navigation bar
 */
import {
  LayoutDashboard,
  Calendar,
  Map,
  Bell,
  Menu,
} from "lucide-react";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import type { Page } from "../../lib/types";

interface MobileNavProps {
  /** Current active page */
  currentPage: Page;
  /** Callback function for page navigation */
  onNavigate: (page: Page) => void;
  /** Optional count of active alerts */
  alertCount?: number;
}

/**
 * Mobile navigation items.
 */
const mobileNavItems: Array<{
  id: Page;
  icon: typeof LayoutDashboard;
  label: string;
  badge?: number;
}> = [
  { id: "dashboard", icon: LayoutDashboard, label: "Home" },
  { id: "schedule", icon: Calendar, label: "Schedule" },
  { id: "fields", icon: Map, label: "Map" },
  { id: "alerts", icon: Bell, label: "Alerts" },
  { id: "settings", icon: Menu, label: "Menu" },
];

export function MobileNav({
  currentPage,
  onNavigate,
  alertCount = 0,
}: MobileNavProps): JSX.Element {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t-2 border-slate-200 md:hidden shadow-lg">
      <div className="grid grid-cols-5 h-16">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          const showBadge = item.id === "alerts" && alertCount > 0;

          return (
            <Button
              key={item.id}
              variant="ghost"
              className={`flex flex-col items-center justify-center h-full rounded-none transition-all duration-200 ${
                isActive ? "text-emerald-600 bg-gradient-to-t from-emerald-100 to-emerald-50 font-semibold" : "text-slate-600 hover:bg-slate-50"
              }`}
              onClick={() => onNavigate(item.id)}
              aria-label={item.label}
            >
              <div className="relative">
                <Icon className="h-5 w-5" />
                {showBadge && (
                  <Badge
                    variant="destructive"
                    className="absolute -top-2 -right-2 h-5 w-5 flex items-center justify-center p-0 rounded-full text-xs"
                  >
                    {alertCount > 9 ? "9+" : alertCount}
                  </Badge>
                )}
              </div>
              <span className="text-xs mt-1">{item.label}</span>
            </Button>
          );
        })}
      </div>
    </nav>
  );
}

