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
  /** Optional recommendation data to display (supports both API and Figma formats) */
  recommendation?: Recommendation | {
    agent: string;
    title: string;
    confidence: number;
    reason: string;
    fields: string[];
    duration?: string;
    waterVolume?: string;
    fireRiskImpact?: string;
    waterSaved?: string;
    _apiRecommendation?: Recommendation;
  } | null;
}

export function RecommendationModal({
  open,
  onClose,
  recommendation,
}: RecommendationModalProps): JSX.Element | null {
  const acceptRecommendation = useAcceptRecommendation();

  const handleAccept = () => {
    // Check if this is an API recommendation (has _apiRecommendation or id)
    const apiRec = (recommendation as any)?._apiRecommendation || (recommendation as Recommendation);
    
    if (apiRec && 'id' in apiRec && apiRec.id) {
      acceptRecommendation.mutate(apiRec.id, {
        onSuccess: () => {
          toast.success("Recommendation accepted and scheduled");
          onClose();
        },
      });
    } else {
      // Demo/Figma format - just show success
      toast.success("Recommendation accepted and scheduled");
      onClose();
    }
  };

  const handleDismiss = () => {
    toast.info("Recommendation dismissed");
    onClose();
  };

  if (!recommendation) return null;

  // Check if this is API format or Figma format
  const isApiFormat = 'id' in recommendation && 'agent_type' in recommendation;
  const isFigmaFormat = 'agent' in recommendation && 'confidence' in recommendation && typeof recommendation.confidence === 'number';

  // Convert confidence from 0-1 to 0-100 for display (API format) or use directly (Figma format)
  const confidencePercent = isApiFormat 
    ? Math.round(((recommendation as Recommendation).confidence || 0) * 100)
    : (recommendation as any).confidence;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{recommendation.title}</DialogTitle>
          <DialogDescription>
            Recommended by {isApiFormat 
              ? (recommendation as Recommendation).agent_type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())
              : (recommendation as any).agent}
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

          {/* Affected Fields */}
          <div>
            <p className="text-slate-600 mb-2">Affected Fields</p>
            {isFigmaFormat ? (
              <div className="flex flex-wrap gap-2">
                {(recommendation as any).fields.map((field: string) => (
                  <Badge key={field} variant="outline">
                    {field}
                  </Badge>
                ))}
              </div>
            ) : (
              <Badge variant="outline">{(recommendation as Recommendation).field_id}</Badge>
            )}
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg">
            {isFigmaFormat ? (
              <>
                {(recommendation as any).duration && (
                  <div>
                    <p className="text-slate-600 mb-1">Duration</p>
                    <p className="text-slate-900">{(recommendation as any).duration}</p>
                  </div>
                )}
                {(recommendation as any).waterVolume && (
                  <div>
                    <p className="text-slate-600 mb-1">Water Volume</p>
                    <p className="text-slate-900">{(recommendation as any).waterVolume}</p>
                  </div>
                )}
                {(recommendation as any).fireRiskImpact && (
                  <div>
                    <p className="text-slate-600 mb-1">Fire Risk Impact</p>
                    <p className="text-emerald-600">{(recommendation as any).fireRiskImpact}</p>
                  </div>
                )}
                {(recommendation as any).waterSaved && (
                  <div>
                    <p className="text-slate-600 mb-1">Water Saved</p>
                    <p className="text-blue-600">{(recommendation as any).waterSaved}</p>
                  </div>
                )}
              </>
            ) : (
              <>
                {(recommendation as Recommendation).fire_risk_reduction_percent !== null && (
                  <div>
                    <p className="text-slate-600 mb-1">Fire Risk Impact</p>
                    <p className="text-emerald-600">
                      ↓ {(recommendation as Recommendation).fire_risk_reduction_percent?.toFixed(0)}% reduction
                    </p>
                  </div>
                )}
                {(recommendation as Recommendation).water_saved_liters !== null && (
                  <div>
                    <p className="text-slate-600 mb-1">Water Volume</p>
                    <p className="text-slate-900">
                      {(recommendation as Recommendation).water_saved_liters?.toLocaleString()} liters
                    </p>
                  </div>
                )}
                {(recommendation as Recommendation).psps_alert && (
                  <div className="col-span-2">
                    <Badge variant="destructive">PSPS Alert</Badge>
                    <p className="text-slate-600 mt-1">This recommendation is related to a Public Safety Power Shutoff event.</p>
                  </div>
                )}
              </>
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
