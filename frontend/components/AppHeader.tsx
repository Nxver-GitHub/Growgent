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
import { toast } from "sonner";

interface AppHeaderProps {
  /** Optional farm name to display */
  farmName?: string;
  /** Optional count of notifications */
  notificationCount?: number;
  /** Optional callback when notification bell is clicked */
  onNotificationClick?: () => void;
  /** Optional callback to toggle sidebar */
  onToggleSidebar?: () => void;
  /** Whether the sidebar is currently open */
  sidebarOpen?: boolean;
}

export function AppHeader({
  farmName = "Sunnydale Farm",
  notificationCount = 0,
  onNotificationClick,
  onToggleSidebar,
  sidebarOpen = true,
}: AppHeaderProps): JSX.Element {
  return (
    <header className="h-16 bg-white border-b-2 border-slate-200 px-6 flex items-center justify-between shadow-sm relative z-[105]">
      <div className="flex items-center gap-4 flex-1">
        {onToggleSidebar && (
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onToggleSidebar} 
            className="hover:bg-emerald-50"
            aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
          >
            <Menu className="h-5 w-5 text-slate-700" />
          </Button>
        )}
        <h1 className="text-2xl font-bold text-slate-900">{farmName}</h1>
      </div>

      <div className="flex items-center gap-4">
        <Button 
          variant="ghost" 
          size="icon" 
          className="relative hover:bg-emerald-50" 
          onClick={onNotificationClick}
        >
          <Bell className="h-5 w-5 text-slate-700" />
          {notificationCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 rounded-full bg-red-500 text-white shadow-md animate-pulse"
            >
              {notificationCount}
            </Badge>
          )}
        </Button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="gap-2 hover:bg-emerald-50">
              <Avatar className="h-9 w-9 border-2 border-emerald-200">
                <AvatarFallback className="bg-gradient-to-br from-emerald-500 to-sky-500 text-white font-semibold shadow-sm">JD</AvatarFallback>
              </Avatar>
              <span className="text-slate-800 font-medium">John Doe</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuLabel>My Account</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => toast.info("Opening profile settings...")}>
              <User className="h-4 w-4 mr-2" />
              Profile
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => toast.info("Opening settings...")}>
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem 
              className="text-red-600"
              onClick={() => toast.info("Logout functionality coming soon")}
            >
              Log out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
