import { useState } from "react";
import { Button } from "./ui/button";
import { AgentStatusCard } from "./AgentStatusCard";
import { MetricWidget } from "./MetricWidget";
import { AlertCard } from "./AlertCard";
import { RecommendationModal } from "./RecommendationModal";
import { Flame, Droplet, Shield, Zap } from "lucide-react";
import { toast } from "sonner";

interface DashboardProps {
  onNavigate: (page: string) => void;
  onDismissAlert?: () => void;
}

export function Dashboard({ onNavigate, onDismissAlert }: DashboardProps) {
  const [visibleAlerts, setVisibleAlerts] = useState([0, 1, 2]);
  const [selectedRecommendation, setSelectedRecommendation] = useState<any>(null);
  const handleAgentClick = (title: string) => {
    if (title === "Fire-Adaptive Irrigation") {
      setSelectedRecommendation({
        agent: "Fire-Adaptive Irrigation Agent",
        title: "Increase Irrigation for Drought Preparation",
        confidence: 92,
        reason: "Pre-PSPS watering recommended. Soil moisture below 40%, drought risk high, fire risk moderate. Strategic watering will protect crops and create defensive moisture barrier.",
        fields: ["Field 1", "Field 3"],
        duration: "2 hours",
        waterVolume: "15,000 liters",
        fireRiskImpact: "↓ 14% reduction",
        waterSaved: "8% more efficient",
      });
    } else if (title === "Utility Shutoff Alert") {
      setSelectedRecommendation({
        agent: "PSPS Anticipation Agent",
        title: "Pre-PSPS Emergency Watering",
        confidence: 95,
        reason: "Public Safety Power Shutoff predicted Nov 9, 14:00-02:00. Immediate pre-irrigation recommended to ensure crop survival during 12-hour power outage.",
        fields: ["Field 1", "Field 2", "Field 3"],
        duration: "3 hours",
        waterVolume: "28,000 liters",
        fireRiskImpact: "↓ 22% reduction",
        waterSaved: "Emergency protocol",
      });
    } else {
      onNavigate("agents");
    }
  };

  const agentCards = [
    {
      icon: Flame,
      title: "Fire-Adaptive Irrigation",
      status: "warning" as const,
      metric: "3 zones ready for watering",
      alertCount: 1,
      lastUpdate: "Updated 2 hours ago",
    },
    {
      icon: Droplet,
      title: "Water Efficiency",
      status: "active" as const,
      metric: "Saved 15,000 liters this season",
      lastUpdate: "Updated 1 hour ago",
    },
    {
      icon: Shield,
      title: "Fire Risk Reduction",
      status: "active" as const,
      metric: "22% fire spread reduction",
      lastUpdate: "Updated 3 hours ago",
    },
    {
      icon: Zap,
      title: "Utility Shutoff Alert",
      status: "warning" as const,
      metric: "PSPS predicted Nov 9, 14:00",
      alertCount: 1,
      lastUpdate: "Updated 30 min ago",
    },
  ];

  const handleDismiss = (index: number) => {
    setVisibleAlerts(visibleAlerts.filter((i) => i !== index));
    onDismissAlert?.();
    toast.success("Alert dismissed");
  };

  const alerts = [
    {
      severity: "critical" as const,
      title: "Irrigation Needed",
      description: "Field 1: Soil moisture <40%, fire risk high. Recommend immediate pre-PSPS watering.",
      time: "2 hours ago",
      fields: ["Field 1", "Field 3"],
    },
    {
      severity: "warning" as const,
      title: "PSPS Event Predicted",
      description: "Public Safety Power Shutoff predicted Nov 9, 14:00-02:00 in your area.",
      time: "3 hours ago",
    },
    {
      severity: "info" as const,
      title: "Crop Health Update",
      description: "Field 2 NDVI improved to 0.75. Irrigation schedule working well.",
      time: "5 hours ago",
      fields: ["Field 2"],
    },
  ];

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
          <Button
            variant="outline"
            onClick={() => onNavigate("chat")}
          >
            Chat with Agents
          </Button>
        </div>
      </div>

      {/* Agent Status Cards */}
      <div>
        <h3 className="mb-4">Agent Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agentCards.map((card, index) => (
            <AgentStatusCard
              key={index}
              {...card}
              onClick={() => handleAgentClick(card.title)}
            />
          ))}
        </div>
      </div>

      {/* Recent Alerts */}
      {visibleAlerts.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3>Recent Alerts</h3>
            <Button
              variant="ghost"
              onClick={() => onNavigate("alerts")}
            >
              View All
            </Button>
          </div>
          <div className="space-y-4">
            {alerts
              .filter((_, index) => visibleAlerts.includes(index))
              .map((alert, arrayIndex) => {
                const originalIndex = visibleAlerts[arrayIndex];
                return (
                  <AlertCard
                    key={originalIndex}
                    {...alert}
                    onDismiss={() => handleDismiss(originalIndex)}
                    onView={() => onNavigate("alerts")}
                  />
                );
              })}
          </div>
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
