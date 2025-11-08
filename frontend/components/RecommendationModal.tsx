/**
 * RecommendationModal component displays detailed agent recommendations.
 *
 * Shows recommendation details, confidence score, and allows accepting or dismissing.
 *
 * @component
 * @param {RecommendationModalProps} props - Component props
 * @returns {JSX.Element} The recommendation modal dialog
 */
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { toast } from "sonner";
import type { Recommendation } from "../lib/types";
import { useAcceptRecommendation } from "../lib/hooks/useRecommendations";
import { formatDate, formatTime } from "../lib/utils/formatters";

interface RecommendationModalProps {
  /** Whether the modal is open */
  open: boolean;
  /** Callback to close the modal */
  onClose: () => void;
  /** Optional recommendation data to display */
  recommendation?: Recommendation | null;
}

export function RecommendationModal({
  open,
  onClose,
  recommendation,
}: RecommendationModalProps): JSX.Element | null {
  const acceptRecommendation = useAcceptRecommendation();

  const handleAccept = () => {
    if (recommendation?.id) {
      acceptRecommendation.mutate(recommendation.id, {
        onSuccess: () => {
          onClose();
        },
      });
    }
  };

  const handleDismiss = () => {
    toast.info("Recommendation dismissed");
    onClose();
  };

  if (!recommendation) return null;

  // Convert confidence from 0-1 to 0-100 for display
  const confidencePercent = Math.round((recommendation.confidence || 0) * 100);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{recommendation.title}</DialogTitle>
          <DialogDescription>
            Recommended by {recommendation.agent_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Confidence */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-600">Confidence</p>
              <p className="text-slate-900">{confidencePercent}%</p>
            </div>
            <Progress value={confidencePercent} className="h-2" />
          </div>

          {/* Reason */}
          <div>
            <p className="text-slate-600 mb-2">Reason</p>
            <p className="text-slate-900">{recommendation.reason}</p>
          </div>

          {/* Affected Field */}
          <div>
            <p className="text-slate-600 mb-2">Field ID</p>
            <Badge variant="outline">{recommendation.field_id}</Badge>
          </div>

          {/* Recommended Timing */}
          {recommendation.recommended_timing && (
            <div>
              <p className="text-slate-600 mb-1">Recommended Timing</p>
              <p className="text-slate-900">
                {formatDate(recommendation.recommended_timing)} at{" "}
                {formatTime(recommendation.recommended_timing)}
              </p>
            </div>
          )}

          {/* Zones Affected */}
          {recommendation.zones_affected && (
            <div>
              <p className="text-slate-600 mb-1">Zones Affected</p>
              <p className="text-slate-900">{recommendation.zones_affected}</p>
            </div>
          )}

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg">
            {recommendation.fire_risk_reduction_percent !== null && (
              <div>
                <p className="text-slate-600 mb-1">Fire Risk Reduction</p>
                <p className="text-emerald-600">
                  ↓ {recommendation.fire_risk_reduction_percent.toFixed(1)}%
                </p>
              </div>
            )}
            {recommendation.water_saved_liters !== null && (
              <div>
                <p className="text-slate-600 mb-1">Water Saved</p>
                <p className="text-blue-600">
                  {recommendation.water_saved_liters.toLocaleString()} liters
                </p>
              </div>
            )}
            {recommendation.psps_alert && (
              <div className="col-span-2">
                <Badge variant="destructive">PSPS Alert</Badge>
                <p className="text-slate-600 mt-1">This recommendation is related to a Public Safety Power Shutoff event.</p>
              </div>
            )}
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleDismiss}>
            Dismiss
          </Button>
          <Button variant="outline" onClick={onClose}>
            Reschedule
          </Button>
          <Button onClick={handleAccept} className="bg-emerald-600 hover:bg-emerald-700">
            Accept Recommendation
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
