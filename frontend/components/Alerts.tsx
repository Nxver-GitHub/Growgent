/**
 * Alerts component displays and manages all farm alerts.
 *
 * Provides filtering, sorting, and dismissal functionality for alerts.
 *
 * @component
 * @param {AlertsProps} props - Component props
 * @returns {JSX.Element} The alerts management view
 */
import { useState, useCallback, useMemo } from "react";
import { AlertCard } from "./AlertCard";
import { Button } from "./ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { toast } from "sonner";
import type { AlertSeverity, Alert } from "../lib/types";
import { useAlerts, useAcknowledgeAlert } from "../lib/hooks/useAlerts";
import { formatRelativeTime } from "../lib/utils/formatters";

interface AlertsProps {
  /** Optional callback when an alert is dismissed */
  onDismissAlert?: () => void;
}

export function Alerts({ onDismissAlert }: AlertsProps): JSX.Element {
  const [filter, setFilter] = useState<"all" | AlertSeverity>("all");
  const [sortBy, setSortBy] = useState<"newest" | "oldest" | "severity" | "field">("newest");
  const [page, setPage] = useState(1);

  // Fetch alerts from API
  const { data: alertsData, isLoading, error } = useAlerts(
    {
      severity: filter === "all" ? undefined : filter,
      acknowledged: false, // Only show unacknowledged alerts
      page,
      page_size: 20,
    },
    { enablePolling: true }
  );

  const acknowledgeAlert = useAcknowledgeAlert();

  // Transform API alerts to component format
  const alerts = useMemo(() => {
    if (!alertsData?.alerts) return [];
    return alertsData.alerts.map((alert: Alert) => ({
      id: alert.id,
      severity: alert.severity,
      title: alert.message.split(":")[0] || alert.message.substring(0, 50),
      description: alert.message,
      time: formatRelativeTime(alert.created_at),
      fields: alert.field_id ? [alert.field_id] : undefined,
    }));
  }, [alertsData]);

  // Sort alerts
  const sortedAlerts = useMemo(() => {
    const sorted = [...alerts];
    switch (sortBy) {
      case "newest":
        return sorted.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());
      case "oldest":
        return sorted.sort((a, b) => new Date(a.time).getTime() - new Date(b.time).getTime());
      case "severity":
        const severityOrder = { critical: 0, warning: 1, info: 2 };
        return sorted.sort(
          (a, b) => severityOrder[a.severity] - severityOrder[b.severity]
        );
      default:
        return sorted;
    }
  }, [alerts, sortBy]);

  const handleDismiss = useCallback(
    (id: string) => {
      acknowledgeAlert.mutate(id);
      onDismissAlert?.();
    },
    [acknowledgeAlert, onDismissAlert]
  );

  const handleMarkAllRead = useCallback(() => {
    // Acknowledge all visible alerts
    alerts.forEach((alert) => {
      acknowledgeAlert.mutate(alert.id);
    });
    toast.success("All alerts acknowledged");
  }, [alerts, acknowledgeAlert]);

  // Show skeleton loaders while loading
  if (isLoading && !alertsData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="h-8 w-48 bg-slate-200 rounded animate-pulse" />
          <div className="h-10 w-32 bg-slate-200 rounded animate-pulse" />
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-24 bg-slate-200 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-red-600 mb-2">Failed to load alerts</p>
        <p className="text-slate-500 text-sm">
          {error instanceof Error ? error.message : "Unknown error"}
        </p>
        <Button className="mt-4" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  const activeAlerts = sortedAlerts;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2>Alerts & Notifications</h2>
          <p className="text-slate-600">Manage all farm alerts and recommendations</p>
        </div>
        <Button variant="outline" onClick={handleMarkAllRead} disabled={activeAlerts.length === 0}>
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

        <Select value={sortBy} onValueChange={(value) => setSortBy(value as typeof sortBy)}>
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
      {activeAlerts.length > 0 ? (
        <>
          <div className="space-y-4">
            {activeAlerts.map((alert) => (
              <AlertCard
                key={alert.id}
                {...alert}
                onDismiss={() => handleDismiss(alert.id)}
                onView={() => toast.info("Viewing alert details")}
              />
            ))}
          </div>

          {/* Pagination */}
          {alertsData && alertsData.total > alertsData.page_size && (
            <div className="flex justify-center items-center gap-4 pt-4">
              <Button
                variant="outline"
                disabled={page === 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                Previous
              </Button>
              <span className="text-slate-600">
                Page {page} of {Math.ceil(alertsData.total / alertsData.page_size)}
              </span>
              <Button
                variant="outline"
                disabled={page >= Math.ceil(alertsData.total / alertsData.page_size)}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
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
