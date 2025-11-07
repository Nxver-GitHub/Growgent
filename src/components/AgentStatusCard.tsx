import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { LucideIcon } from "lucide-react";

interface AgentStatusCardProps {
  icon: LucideIcon;
  title: string;
  status: "active" | "warning" | "error";
  metric: string;
  alertCount?: number;
  lastUpdate: string;
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
}: AgentStatusCardProps) {
  const statusColors = {
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
