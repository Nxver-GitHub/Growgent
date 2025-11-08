/**
 * PSPSAlert component for checking and displaying Public Safety Power Shutoff alerts.
 *
 * @component
 */
import { useState } from "react";
import { Button } from "./ui/button";
import { Zap, Loader, AlertTriangle } from "lucide-react";
import { toast } from "sonner";

// A dummy field ID for now. In a real app, this would come from user context or selection.
const DUMMY_FIELD_ID = "a1b2c3d4-e5f6-7890-1234-567890abcdef";

export function PSPSAlert() {
  const [isLoading, setIsLoading] = useState(false);
  const [alert, setAlert] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckForPSPS = async () => {
    setIsLoading(true);
    setAlert(null);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/agents/utility-shutoff/check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          field_id: DUMMY_FIELD_ID,
          latitude: 38.5, // Dummy coordinates for now
          longitude: -122.5,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to check for PSPS events.");
      }

      const result = await response.json();

      if (result.status === "success" && result.data.alert_generated) {
        setAlert(result.data.alert_message);
        toast.warning(result.data.alert_message);
      } else {
        setAlert("No high-confidence PSPS events predicted at this time.");
        toast.success("No high-confidence PSPS events predicted.");
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An unknown error occurred.";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-slate-50 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Zap className="w-6 h-6 text-yellow-500" />
          <h4 className="font-semibold">PSPS Watch</h4>
        </div>
        <Button onClick={handleCheckForPSPS} disabled={isLoading}>
          {isLoading ? (
            <Loader className="w-4 h-4 animate-spin" />
          ) : (
            "Check for PSPS Events"
          )}
        </Button>
      </div>
      {alert && (
        <div className="mt-4 text-sm text-slate-700 p-3 bg-yellow-100 border border-yellow-200 rounded-md">
          {alert}
        </div>
      )}
      {error && (
        <div className="mt-4 text-sm text-red-700 p-3 bg-red-100 border border-red-200 rounded-md flex items-center gap-2">
          <AlertTriangle className="w-4 h-4" />
          {error}
        </div>
      )}
    </div>
  );
}
