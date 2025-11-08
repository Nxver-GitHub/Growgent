/**
 * MetricWidget component displays a single metric with optional trend indicator.
 *
 * Shows a label, value, and optional trend direction with icon.
 *
 * @component
 * @param {MetricWidgetProps} props - Component props
 * @returns {JSX.Element} The metric widget card
 */
import { Card } from "./ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import type { TrendDirection } from "../lib/types";

interface MetricWidgetProps {
  /** Label for the metric */
  label: string;
  /** Current value to display */
  value: string;
  /** Optional trend direction */
  trend?: TrendDirection;
  /** Optional trend value text */
  trendValue?: string;
  /** Optional additional CSS classes */
  className?: string;
}

export function MetricWidget({
  label,
  value,
  trend,
  trendValue,
  className = "",
}: MetricWidgetProps): JSX.Element {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  
  const getTrendStyles = () => {
    if (trend === "up") {
      return {
        color: "text-green-600",
        bg: "bg-green-50",
        iconBg: "bg-green-100",
      };
    }
    if (trend === "down") {
      return {
        color: "text-red-600",
        bg: "bg-red-50",
        iconBg: "bg-red-100",
      };
    }
    return {
      color: "text-slate-600",
      bg: "bg-slate-50",
      iconBg: "bg-slate-100",
    };
  };

  const styles = getTrendStyles();

  return (
    <Card className={`p-6 border-2 border-slate-200 hover:border-emerald-300 transition-all duration-200 hover:shadow-lg ${className}`}>
      <p className="text-slate-600 text-sm font-medium mb-3 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-bold text-slate-900 mb-3">{value}</p>
      {trend && trendValue && (
        <div className={`flex items-center gap-2 ${styles.bg} ${styles.color} px-3 py-1.5 rounded-lg w-fit`}>
          <div className={`${styles.iconBg} p-1 rounded`}>
            <TrendIcon className="h-3.5 w-3.5" />
          </div>
          <span className="text-sm font-semibold">{trendValue}</span>
        </div>
      )}
    </Card>
  );
}
