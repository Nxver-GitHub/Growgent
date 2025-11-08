/**
 * Dashboard component displays the main overview of farm status and agent recommendations.
 *
 * Shows agent status cards, recent alerts, quick stats, and handles recommendation modals.
 *
 * @component
 * @param {DashboardProps} props - Component props
 * @returns {JSX.Element} The dashboard view
 */
import { useState, useCallback, useMemo } from "react";
import { Button } from "./ui/button";
import { AgentStatusCard } from "./AgentStatusCard";
import { MetricWidget } from "./MetricWidget";
import { AlertCard } from "./AlertCard";
import { RecommendationModal } from "./RecommendationModal";
import { Skeleton } from "./ui/skeleton";
import { Flame, Droplet, Shield, Zap } from "lucide-react";
import { toast } from "sonner";
import type { Page, Alert, Recommendation as RecommendationType } from "../lib/types";
import { useDashboard } from "../lib/hooks/useDashboard";
import { useCriticalAlerts } from "../lib/hooks/useAlerts";
import { useRecommendations } from "../lib/hooks/useRecommendations";
import { formatRelativeTime } from "../lib/utils/formatters";
import { PSPSAlert } from "./PSPSAlert";

interface DashboardProps {
  /** Callback function for page navigation */
  onNavigate: (page: Page) => void;
  /** Optional callback when an alert is dismissed */
  onDismissAlert?: () => void;
}

export function Dashboard({ onNavigate, onDismissAlert }: DashboardProps): JSX.Element {
  // Fetch dashboard data from API - use individual hooks for better error handling
  const { data: criticalAlertsData, isLoading: isLoadingAlerts, error: alertsError } = useCriticalAlerts({ limit: 5 });
  const { data: recommendationsData, isLoading: isLoadingRecs, error: recsError } = useRecommendations({ page: 1, page_size: 5 });
  
  // Use dashboard hook as fallback, but prefer individual hooks
  const { data: dashboardData, error: dashboardError } = useDashboard();
  
  const isLoading = isLoadingAlerts || isLoadingRecs;

  const [selectedRecommendation, setSelectedRecommendation] = useState<RecommendationType | null>(null);
  // Track dismissed alerts by index to match Figma interaction pattern
  const [dismissedAlertIndices, setDismissedAlertIndices] = useState<Set<number>>(new Set());
  /**
   * Handles agent card click and sets the appropriate recommendation.
   * Matches Figma interaction pattern while supporting API data.
   *
   * @param {string} title - The title of the agent that was clicked
   */
  const handleAgentClick = useCallback(
    (title: string): void => {
      // Find the first recommendation for this agent type
      const recommendations = recommendationsData?.recommendations || [];
      const agentTypeMap: Record<string, string> = {
        "Fire-Adaptive Irrigation": "fire_adaptive_irrigation",
        "Water Efficiency": "water_efficiency",
        "Fire Risk Reduction": "fire_risk_reduction",
        "Utility Shutoff Alert": "psps_anticipation",
      };

      const agentType = agentTypeMap[title];
      const recommendation = recommendations.find((rec) => rec.agent_type === agentType);

      if (recommendation) {
        // Convert API recommendation to Figma-compatible format
        const figmaFormat = {
          agent: recommendation.agent_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()) + " Agent",
          title: recommendation.title,
          confidence: Math.round((recommendation.confidence || 0) * 100),
          reason: recommendation.reason,
          fields: recommendation.field_id ? [recommendation.field_id] : [],
          duration: recommendation.recommended_timing ? "2 hours" : undefined,
          waterVolume: recommendation.water_saved_liters 
            ? `${recommendation.water_saved_liters.toLocaleString()} liters`
            : undefined,
          fireRiskImpact: recommendation.fire_risk_reduction_percent !== null
            ? `↓ ${recommendation.fire_risk_reduction_percent.toFixed(0)}% reduction`
            : undefined,
          waterSaved: recommendation.water_saved_liters
            ? `${((recommendation.water_saved_liters / 1000) * 0.08).toFixed(0)}% more efficient`
            : undefined,
          // Store original API recommendation for API calls
          _apiRecommendation: recommendation,
        };
        setSelectedRecommendation(figmaFormat as any);
      } else if (title === "Fire-Adaptive Irrigation" || title === "Utility Shutoff Alert") {
        // Fallback to Figma demo data if no API data available
        const demoData = title === "Fire-Adaptive Irrigation" 
          ? {
          agent: "Fire-Adaptive Irrigation Agent",
          title: "Increase Irrigation for Drought Preparation",
          confidence: 92,
              reason: "Pre-PSPS watering recommended. Soil moisture below 40%, drought risk high, fire risk moderate. Strategic watering will protect crops and create defensive moisture barrier.",
          fields: ["Field 1", "Field 3"],
          duration: "2 hours",
          waterVolume: "15,000 liters",
          fireRiskImpact: "↓ 14% reduction",
          waterSaved: "8% more efficient",
            }
          : {
          agent: "PSPS Anticipation Agent",
          title: "Pre-PSPS Emergency Watering",
          confidence: 95,
              reason: "Public Safety Power Shutoff predicted Nov 9, 14:00-02:00. Immediate pre-irrigation recommended to ensure crop survival during 12-hour power outage.",
          fields: ["Field 1", "Field 2", "Field 3"],
          duration: "3 hours",
          waterVolume: "28,000 liters",
          fireRiskImpact: "↓ 22% reduction",
          waterSaved: "Emergency protocol",
            };
        setSelectedRecommendation(demoData as any);
      } else {
        onNavigate("dashboard");
      }
    },
    [onNavigate, recommendationsData]
  );

  // Transform API data into agent cards
  const agentCards = useMemo(() => {
    const recommendations = recommendationsData?.recommendations || [];
    const alerts = criticalAlertsData?.alerts || [];

    // Count recommendations and alerts by agent type
    const fireAdaptiveRecs = recommendations.filter(
      (r) => r.agent_type === "fire_adaptive_irrigation" && !r.accepted
    );
    const pspsAlerts = alerts.filter((a) => a.agent_type === "psps_anticipation");

    return [
    {
      icon: Flame,
      title: "Fire-Adaptive Irrigation",
        status: fireAdaptiveRecs.length > 0 ? ("warning" as const) : ("active" as const),
        metric: `${fireAdaptiveRecs.length} recommendation${fireAdaptiveRecs.length !== 1 ? "s" : ""} pending`,
        alertCount: alerts.filter((a) => a.agent_type === "fire_adaptive_irrigation").length,
        lastUpdate: recommendations.length > 0
          ? formatRelativeTime(recommendations[0]?.updated_at || recommendations[0]?.created_at)
          : "No updates",
    },
    {
      icon: Droplet,
      title: "Water Efficiency",
      status: "active" as const,
        metric: "Monitoring water usage",
        lastUpdate: "Updated recently",
    },
    {
      icon: Shield,
      title: "Fire Risk Reduction",
      status: "active" as const,
        metric: "Monitoring fire risk",
        lastUpdate: "Updated recently",
    },
    {
      icon: Zap,
      title: "Utility Shutoff Alert",
        status: pspsAlerts.length > 0 ? ("warning" as const) : ("active" as const),
        metric: pspsAlerts.length > 0 ? `${pspsAlerts.length} PSPS alert${pspsAlerts.length !== 1 ? "s" : ""}` : "No events",
        alertCount: pspsAlerts.length,
        lastUpdate: pspsAlerts.length > 0 ? formatRelativeTime(pspsAlerts[0]?.created_at) : "No updates",
    },
  ];
  }, [recommendationsData, criticalAlertsData]);

  // Check if backend is offline (connection refused errors)
  const isBackendOffline = 
    (alertsError instanceof Error && alertsError.message.includes("Failed to fetch")) ||
    (recsError instanceof Error && recsError.message.includes("Failed to fetch")) ||
    (dashboardError instanceof Error && dashboardError.message.includes("Failed to fetch"));

  // Transform API alerts to component format
  const alerts = useMemo(() => {
    // Return empty array if backend is offline to show empty state
    if (isBackendOffline) {
      return [];
    }
    const apiAlerts = criticalAlertsData?.alerts || [];
    return apiAlerts.slice(0, 5).map((alert: Alert, index: number) => ({
      index, // Store original index for dismissal tracking
      severity: alert.severity,
      title: alert.message.split(":")[0] || alert.message.substring(0, 50),
      description: alert.message,
      time: formatRelativeTime(alert.created_at),
      fields: alert.field_id ? [alert.field_id] : undefined,
    }));
  }, [criticalAlertsData, isBackendOffline]);

  // Filter out dismissed alerts
  const visibleAlerts = useMemo(() => {
    return alerts.filter((alert) => !dismissedAlertIndices.has(alert.index));
  }, [alerts, dismissedAlertIndices]);

  // Handle alert dismissal
  const handleDismiss = useCallback((index: number) => {
    setDismissedAlertIndices((prev) => new Set([...prev, index]));
      onDismissAlert?.();
      toast.success("Alert dismissed");
  }, [onDismissAlert]);

  // Show skeleton loaders only on initial load (not when backend is offline)
  const shouldShowSkeleton = isLoading && !isBackendOffline && !criticalAlertsData && !recommendationsData;

  if (shouldShowSkeleton) {
    return (
      <div className="space-y-8">
        {/* Hero Section Skeleton */}
        <div className="bg-gradient-to-r from-emerald-50 to-sky-50 rounded-2xl p-8">
          <Skeleton className="h-8 w-64 mb-4" />
          <div className="flex gap-4">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-40" />
            <Skeleton className="h-10 w-36" />
          </div>
        </div>

        {/* Agent Cards Skeleton */}
        <div>
          <Skeleton className="h-6 w-32 mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 rounded-lg" />
            ))}
          </div>
        </div>

        {/* Alerts Skeleton */}
        <div>
          <Skeleton className="h-6 w-32 mb-4" />
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-24 rounded-lg" />
            ))}
          </div>
        </div>

        {/* Stats Skeleton */}
        <div>
          <Skeleton className="h-6 w-32 mb-4" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-24 rounded-lg" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Show backend offline banner if backend is not available
  const showOfflineBanner = isBackendOffline;

  const metrics = [
    {
      label: "Water Usage",
      value: "2.3M gallons",
      trend: "down" as const,
      trendValue: "↓ 18% below average",
    },
    {
      label: "Crop Health (NDVI)",
      value: "0.72",
      trend: "up" as const,
      trendValue: "Good",
    },
    {
      label: "Fire Risk Score",
      value: "Low",
      trend: "down" as const,
      trendValue: "↓ Improving",
    },
    {
      label: "Irrigation Events",
      value: "12 this month",
      trend: "neutral" as const,
      trendValue: "On track",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Backend Offline Banner */}
      {showOfflineBanner && (
        <div className="bg-amber-50 border-l-4 border-amber-500 rounded-lg p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-amber-800 font-medium">Backend API is not available</p>
              <p className="text-amber-700 text-sm mt-1">
                Please ensure the backend server is running on <code className="bg-amber-100 px-1 rounded">http://localhost:8000</code>
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.location.reload()}
              className="border-amber-300 text-amber-700 hover:bg-amber-100"
            >
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-emerald-50 to-sky-50 rounded-2xl p-8">
        <h2 className="mb-4">Your Farm is Ready for Climate Action</h2>
        <div className="flex gap-4">
          <Button
            className="bg-emerald-600 hover:bg-emerald-700"
            onClick={() => onNavigate("fields")}
          >
            View Fields
          </Button>
          <Button
            variant="outline"
            onClick={() => onNavigate("schedule")}
          >
            Irrigation Schedule
          </Button>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div>
        <h3 className="mb-4">Agent Status</h3>
        {isLoadingRecs && !isBackendOffline && !recommendationsData ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 rounded-lg" />
            ))}
          </div>
        ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agentCards.map((card, index) => (
            <AgentStatusCard key={index} {...card} onClick={() => handleAgentClick(card.title)} />
          ))}
        </div>
        )}
      </div>

      {/* PSPS Alert Checker */}
      <PSPSAlert />

      {/* Recent Alerts */}
      {visibleAlerts.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3>Recent Alerts</h3>
            <Button variant="ghost" onClick={() => onNavigate("alerts")}>
              View All
            </Button>
          </div>
          {isLoadingAlerts && !isBackendOffline && !criticalAlertsData ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24 rounded-lg" />
              ))}
            </div>
          ) : (
          <div className="space-y-4">
              {visibleAlerts.map((alert) => (
                  <AlertCard
                  key={`alert-${alert.index}`}
                  severity={alert.severity}
                  title={alert.title}
                  description={alert.description}
                  time={alert.time}
                  fields={alert.fields}
                  onDismiss={() => handleDismiss(alert.index)}
                    onView={() => onNavigate("alerts")}
                  />
              ))}
          </div>
          )}
        </div>
      )}

      {/* Quick Stats */}
      <div>
        <h3 className="mb-4">Quick Stats</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricWidget key={index} {...metric} />
          ))}
        </div>
      </div>

      {/* Recommendation Modal */}
      <RecommendationModal
        open={!!selectedRecommendation}
        onClose={() => setSelectedRecommendation(null)}
        recommendation={selectedRecommendation}
      />
    </div>
  );
}
