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
  const trendColor =
    trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-slate-600";

  return (
    <Card className={`p-6 ${className}`}>
      <p className="text-slate-600 mb-2">{label}</p>
      <p className="mb-2">{value}</p>
      {trend && trendValue && (
        <div className={`flex items-center gap-1 ${trendColor}`}>
          <TrendIcon className="h-4 w-4" />
          <span>{trendValue}</span>
        </div>
      )}
    </Card>
  );
}
