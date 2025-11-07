/**
 * AppHeader component displays the main application header.
 *
 * Shows farm name, notifications, user menu, and sidebar toggle.
 *
 * @component
 * @param {AppHeaderProps} props - Component props
 * @returns {JSX.Element} The application header
 */
import { Bell, User, Menu } from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Avatar, AvatarFallback } from "./ui/avatar";

interface AppHeaderProps {
  /** Optional farm name to display */
  farmName?: string;
  /** Optional count of notifications */
  notificationCount?: number;
  /** Optional callback when notification bell is clicked */
  onNotificationClick?: () => void;
  /** Optional callback to toggle sidebar */
  onToggleSidebar?: () => void;
  /** Whether the sidebar is currently collapsed */
  sidebarCollapsed?: boolean;
}

export function AppHeader({
  farmName = "Sunnydale Farm",
  notificationCount = 0,
  onNotificationClick,
  onToggleSidebar,
  sidebarCollapsed = false,
}: AppHeaderProps): JSX.Element {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4 flex-1">
        {sidebarCollapsed && onToggleSidebar && (
          <Button variant="ghost" size="icon" onClick={onToggleSidebar}>
            <Menu className="h-5 w-5 text-slate-600" />
          </Button>
        )}
        <h1 className="text-slate-800">{farmName}</h1>
      </div>

      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" className="relative" onClick={onNotificationClick}>
          <Bell className="h-5 w-5 text-slate-600" />
          {notificationCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 rounded-full"
            >
              {notificationCount}
            </Badge>
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2">
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-emerald-100 text-emerald-700">JD</AvatarFallback>
              </Avatar>
              <span className="text-slate-700">John Doe</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="h-4 w-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem>Settings</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-red-600">Log out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
