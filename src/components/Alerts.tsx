import { useState } from "react";
import { AlertCard } from "./AlertCard";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { toast } from "sonner";

interface AlertsProps {
  onDismissAlert?: () => void;
}

export function Alerts({ onDismissAlert }: AlertsProps) {
  const [filter, setFilter] = useState("all");
  const [dismissedAlerts, setDismissedAlerts] = useState<number[]>([]);

  const alerts = [
    {
      id: 1,
      severity: "critical" as const,
      title: "Irrigation Needed",
      description: "Field 1: Soil moisture <40%, fire risk high. Recommend immediate pre-PSPS watering.",
      time: "2 hours ago",
      fields: ["Field 1", "Field 3"],
    },
    {
      id: 2,
      severity: "warning" as const,
      title: "PSPS Event Predicted",
      description: "Public Safety Power Shutoff predicted Nov 9, 14:00-02:00 in your area.",
      time: "3 hours ago",
    },
    {
      id: 3,
      severity: "warning" as const,
      title: "Frost Risk Alert",
      description: "Climate Agent: 78% confidence frost in next 48h. Recommend frost cloth deployment.",
      time: "4 hours ago",
      fields: ["Field 2"],
    },
    {
      id: 4,
      severity: "info" as const,
      title: "Crop Health Update",
      description: "Field 2 NDVI improved to 0.75. Irrigation schedule working well.",
      time: "5 hours ago",
      fields: ["Field 2"],
    },
    {
      id: 5,
      severity: "info" as const,
      title: "Market Opportunity",
      description: "Strawberry prices ↑ 5%. Good time to harvest early based on market intel.",
      time: "6 hours ago",
    },
    {
      id: 6,
      severity: "critical" as const,
      title: "Low Water Reservoir",
      description: "Water reservoir at 35% capacity. Plan for reduced irrigation in next 2 weeks.",
      time: "8 hours ago",
    },
    {
      id: 7,
      severity: "warning" as const,
      title: "Sensor Maintenance Required",
      description: "Soil moisture sensor #3 in Field 1 showing erratic readings. Schedule maintenance.",
      time: "1 day ago",
      fields: ["Field 1"],
    },
    {
      id: 8,
      severity: "info" as const,
      title: "Weather Update",
      description: "No precipitation expected for next 7 days. Continue current irrigation schedule.",
      time: "1 day ago",
    },
  ];

  const handleDismiss = (id: number) => {
    setDismissedAlerts([...dismissedAlerts, id]);
    onDismissAlert?.();
    toast.success("Alert dismissed");
  };

  const handleMarkAllRead = () => {
    const allIds = alerts.map((a) => a.id);
    setDismissedAlerts(allIds);
    toast.success("All alerts marked as read");
  };

  const activeAlerts = alerts.filter((alert) => !dismissedAlerts.includes(alert.id));
  
  const filteredAlerts = activeAlerts.filter((alert) => {
    if (filter === "all") return true;
    return alert.severity === filter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2>Alerts & Notifications</h2>
          <p className="text-slate-600">Manage all farm alerts and recommendations</p>
        </div>
        <Button 
          variant="outline" 
          onClick={handleMarkAllRead}
          disabled={activeAlerts.length === 0}
        >
          Mark All as Read
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <Tabs value={filter} onValueChange={setFilter} className="w-full">
          <TabsList>
            <TabsTrigger value="all">All ({activeAlerts.length})</TabsTrigger>
            <TabsTrigger value="critical">
              Critical ({activeAlerts.filter((a) => a.severity === "critical").length})
            </TabsTrigger>
            <TabsTrigger value="warning">
              Warning ({activeAlerts.filter((a) => a.severity === "warning").length})
            </TabsTrigger>
            <TabsTrigger value="info">
              Info ({activeAlerts.filter((a) => a.severity === "info").length})
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <Select defaultValue="newest">
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Newest First</SelectItem>
            <SelectItem value="oldest">Oldest First</SelectItem>
            <SelectItem value="severity">By Severity</SelectItem>
            <SelectItem value="field">By Field</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Alert List */}
      {filteredAlerts.length > 0 ? (
        <>
          <div className="space-y-4">
            {filteredAlerts.map((alert) => (
              <AlertCard
                key={alert.id}
                {...alert}
                onDismiss={() => handleDismiss(alert.id)}
                onView={() => toast.info("Viewing alert details")}
              />
            ))}
          </div>

          {/* Load More */}
          <div className="flex justify-center pt-4">
            <Button variant="outline">Load More Alerts</Button>
          </div>
        </>
      ) : (
        <div className="text-center py-16">
          <p className="text-slate-600">No alerts to display</p>
          <p className="text-slate-500 mt-2">All caught up! 🎉</p>
        </div>
      )}
    </div>
  );
}
