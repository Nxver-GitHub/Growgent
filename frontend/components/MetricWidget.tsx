import { Card } from "./ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricWidgetProps {
  label: string;
  value: string;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  className?: string;
}

export function MetricWidget({
  label,
  value,
  trend,
  trendValue,
  className = "",
}: MetricWidgetProps) {
  const TrendIcon = trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;
  const trendColor = trend === "up" ? "text-green-600" : trend === "down" ? "text-red-600" : "text-slate-600";

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
