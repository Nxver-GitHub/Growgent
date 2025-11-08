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

  return (
    <Card
      className="p-6 hover:shadow-lg transition-all duration-200 hover:-translate-y-1 cursor-pointer border-slate-200"
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-emerald-50 rounded-lg">
            <Icon className="h-6 w-6 text-emerald-600" />
          </div>
          <div className={`w-3 h-3 rounded-full ${statusColors[status]}`} />
        </div>
        {alertCount && alertCount > 0 && (
          <Badge variant="destructive" className="rounded-full">
            {alertCount}
          </Badge>
        )}
      </div>
      
      <h3 className="mb-2">{title}</h3>
      
      <p className="text-slate-600 mb-4">{metric}</p>
      
      <div className="flex items-center justify-between">
        <span className="text-slate-500">{lastUpdate}</span>
        <Button variant="ghost" size="sm" className="text-emerald-600">
          View Details
        </Button>
      </div>
    </Card>
  );
}
