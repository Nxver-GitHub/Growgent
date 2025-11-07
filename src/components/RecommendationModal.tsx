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

interface RecommendationModalProps {
  open: boolean;
  onClose: () => void;
  recommendation?: {
    agent: string;
    title: string;
    confidence: number;
    reason: string;
    fields: string[];
    duration?: string;
    waterVolume?: string;
    fireRiskImpact?: string;
    waterSaved?: string;
  };
}

export function RecommendationModal({
  open,
  onClose,
  recommendation,
}: RecommendationModalProps) {
  const handleAccept = () => {
    toast.success("Recommendation accepted and scheduled");
    onClose();
  };

  const handleDismiss = () => {
    toast.info("Recommendation dismissed");
    onClose();
  };

  if (!recommendation) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{recommendation.title}</DialogTitle>
          <DialogDescription>
            Recommended by {recommendation.agent}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Confidence */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-slate-600">Confidence</p>
              <p className="text-slate-900">{recommendation.confidence}%</p>
            </div>
            <Progress value={recommendation.confidence} className="h-2" />
          </div>

          {/* Reason */}
          <div>
            <p className="text-slate-600 mb-2">Reason</p>
            <p className="text-slate-900">{recommendation.reason}</p>
          </div>

          {/* Affected Fields */}
          <div>
            <p className="text-slate-600 mb-2">Affected Fields</p>
            <div className="flex flex-wrap gap-2">
              {recommendation.fields.map((field) => (
                <Badge key={field} variant="outline">
                  {field}
                </Badge>
              ))}
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-4 p-4 bg-slate-50 rounded-lg">
            {recommendation.duration && (
              <div>
                <p className="text-slate-600 mb-1">Duration</p>
                <p className="text-slate-900">{recommendation.duration}</p>
              </div>
            )}
            {recommendation.waterVolume && (
              <div>
                <p className="text-slate-600 mb-1">Water Volume</p>
                <p className="text-slate-900">{recommendation.waterVolume}</p>
              </div>
            )}
            {recommendation.fireRiskImpact && (
              <div>
                <p className="text-slate-600 mb-1">Fire Risk Impact</p>
                <p className="text-emerald-600">{recommendation.fireRiskImpact}</p>
              </div>
            )}
            {recommendation.waterSaved && (
              <div>
                <p className="text-slate-600 mb-1">Water Saved</p>
                <p className="text-blue-600">{recommendation.waterSaved}</p>
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
