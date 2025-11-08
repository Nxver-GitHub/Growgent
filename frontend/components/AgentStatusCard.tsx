/**
 * AgentStatusCard component displays the status and metrics for an agent.
 *
 * Shows agent icon, status indicator, current metric, alert count, and last update time.
 * Provides click interaction for viewing agent details.
 *
 * @component
 * @param {AgentStatusCardProps} props - Component props
 * @returns {JSX.Element} The agent status card
 */
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { LucideIcon } from "lucide-react";

interface AgentStatusCardProps {
  /** Lucide icon component to display for the agent */
  icon: LucideIcon;
  /** Title/name of the agent */
  title: string;
  /** Current status of the agent */
  status: "active" | "warning" | "error";
  /** Current metric value to display */
  metric: string;
  /** Optional count of active alerts */
  alertCount?: number;
  /** Timestamp of last update */
  lastUpdate: string;
  /** Optional click handler for card interaction */
  onClick?: () => void;
}

export function AgentStatusCard({
  icon: Icon,
  title,
  status,
  metric,
  alertCount,
  lastUpdate,
  onClick,
}: AgentStatusCardProps): JSX.Element {
  const statusColors: Record<"active" | "warning" | "error", string> = {
    active: "bg-green-500",
    warning: "bg-amber-500",
    error: "bg-red-500",
  };

  // Color schemes for different agent types
  const getIconBgColor = (title: string): string => {
    if (title.includes("Fire")) return "bg-gradient-to-br from-orange-100 to-red-100";
    if (title.includes("Water")) return "bg-gradient-to-br from-blue-100 to-cyan-100";
    if (title.includes("Shutoff")) return "bg-gradient-to-br from-amber-100 to-yellow-100";
    return "bg-gradient-to-br from-emerald-100 to-green-100";
  };

  const getIconColor = (title: string): string => {
    if (title.includes("Fire")) return "text-orange-600";
    if (title.includes("Water")) return "text-blue-600";
    if (title.includes("Shutoff")) return "text-amber-600";
    return "text-emerald-600";
  };

  return (
    <Card
      className="p-6 hover:shadow-xl transition-all duration-300 hover:-translate-y-2 cursor-pointer border-2 border-slate-200 hover:border-emerald-300 bg-white"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`p-3 ${getIconBgColor(title)} rounded-xl shadow-sm`}>
            <Icon className={`h-6 w-6 ${getIconColor(title)}`} />
          </div>
          <div className={`w-3 h-3 rounded-full ${statusColors[status]} shadow-sm`} />
        </div>
        {alertCount && alertCount > 0 && (
          <Badge variant="destructive" className="rounded-full bg-red-500 text-white shadow-sm">
            {alertCount}
          </Badge>
        )}
      </div>

      <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>

      <p className="text-slate-700 mb-4 font-medium">{metric}</p>

      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
        <span className="text-sm text-slate-500">{lastUpdate}</span>
        <Button variant="ghost" size="sm" className="text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50">
          View Details →
        </Button>
      </div>
    </Card>
  );
}
