/**
 * AlertCard component displays an alert notification.
 *
 * Shows alert severity, title, description, affected fields, and action buttons.
 *
 * @component
 * @param {AlertCardProps} props - Component props
 * @returns {JSX.Element} The alert card
 */
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { AlertCircle, AlertTriangle, Info, X } from "lucide-react";
import type { AlertSeverity } from "../lib/types";

interface AlertCardProps {
  /** Severity level of the alert */
  severity: AlertSeverity;
  /** Title of the alert */
  title: string;
  /** Detailed description of the alert */
  description: string;
  /** Timestamp or relative time of the alert */
  time: string;
  /** Optional list of affected field names */
  fields?: string[];
  /** Optional callback when alert is dismissed */
  onDismiss?: () => void;
  /** Optional callback when view details is clicked */
  onView?: () => void;
}

export function AlertCard({
  severity,
  title,
  description,
  time,
  fields,
  onDismiss,
  onView,
}: AlertCardProps): JSX.Element {
  const severityConfig: Record<
    AlertSeverity,
    {
      icon: typeof AlertCircle;
      color: string;
      bgColor: string;
      borderColor: string;
    }
  > = {
    critical: {
      icon: AlertCircle,
      color: "text-red-600",
      bgColor: "bg-red-50",
      borderColor: "border-l-red-500",
    },
    warning: {
      icon: AlertTriangle,
      color: "text-amber-600",
      bgColor: "bg-amber-50",
      borderColor: "border-l-amber-500",
    },
    info: {
      icon: Info,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      borderColor: "border-l-blue-500",
    },
  };

  // Defensive check: ensure severity is valid, default to "info" if not
  const validSeverity: AlertSeverity = 
    severity && severity in severityConfig ? severity : "info";
  const config = severityConfig[validSeverity];
  const Icon = config.icon;

  return (
    <Card className={`p-4 border-l-4 ${config.borderColor} ${config.bgColor}`}>
      <div className="flex items-start gap-3">
        <Icon className={`h-5 w-5 mt-0.5 ${config.color}`} />
        
        <div className="flex-1">
          <div className="flex items-start justify-between mb-1">
            <h4 className={config.color}>{title}</h4>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">{time}</span>
              {onDismiss && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDismiss}
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          
          <p className="text-slate-700 mb-2">{description}</p>
          
          {fields && fields.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {fields.map((field) => (
                <span
                  key={field}
                  className="px-2 py-1 bg-white rounded text-slate-700"
                >
                  {field}
                </span>
              ))}
            </div>
          )}
          
          {onView && (
            <Button variant="outline" size="sm" onClick={onView}>
              View Details
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
