/**
 * AddZoneDialog component for creating and editing risk zones on the map.
 *
 * Allows users to:
 * - Name the zone
 * - Select zone type (fire risk, PSPS, irrigation, custom)
 * - Select risk level
 * - Draw or input coordinates for the zone boundary
 * - Edit existing zones
 *
 * @component
 */

import { useState, useCallback, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { Textarea } from "./ui/textarea";
import { AlertCircle, Zap, Droplet, MapPin } from "lucide-react";
import type { ZoneType, ZoneLevel, RiskZone } from "../lib/types";

interface AddZoneDialogProps {
  /** Whether the dialog is open */
  open: boolean;
  /** Callback when dialog should close */
  onOpenChange: (open: boolean) => void;
  /** Callback when zone is created */
  onCreateZone: (zone: {
    name: string;
    type: ZoneType;
    level: ZoneLevel;
    geometry: GeoJSON.Feature;
    description?: string;
  }) => void;
  /** Callback when zone is updated (for edit mode) */
  onUpdateZone?: (zoneId: string, zone: {
    name: string;
    type: ZoneType;
    level: ZoneLevel;
    geometry: GeoJSON.Feature;
    description?: string;
  }) => void;
  /** Zone to edit (if in edit mode) */
  editingZone?: RiskZone | null;
  /** Whether drawing mode is active on the map */
  drawingMode?: boolean;
  /** Callback to toggle drawing mode */
  onToggleDrawing?: () => void;
  /** Current drawn geometry (if any) */
  drawnGeometry?: GeoJSON.Feature | null;
}

export function AddZoneDialog({
  open,
  onOpenChange,
  onCreateZone,
  onUpdateZone,
  editingZone = null,
  drawingMode = false,
  onToggleDrawing,
  drawnGeometry,
}: AddZoneDialogProps): JSX.Element {
  const [name, setName] = useState("");
  const [type, setType] = useState<ZoneType>("fire_risk");
  const [level, setLevel] = useState<ZoneLevel>("moderate");
  const [description, setDescription] = useState("");

  // Populate form when editing
  useEffect(() => {
    if (editingZone) {
      setName(editingZone.name);
      setType(editingZone.type);
      setLevel(editingZone.level);
      setDescription(editingZone.description || "");
    } else {
      // Reset form for new zone
      setName("");
      setType("fire_risk");
      setLevel("moderate");
      setDescription("");
    }
  }, [editingZone, open]);

  // Hide Mapbox controls when dialog is open
  useEffect(() => {
    if (open) {
      document.body.classList.add("dialog-open");
      // Force hide Mapbox controls
      const style = document.createElement("style");
      style.id = "mapbox-controls-hide";
      style.textContent = `
        .mapboxgl-control-container,
        .mapboxgl-ctrl-group,
        .mapboxgl-ctrl {
          display: none !important;
        }
      `;
      document.head.appendChild(style);
    } else {
      document.body.classList.remove("dialog-open");
      const style = document.getElementById("mapbox-controls-hide");
      if (style) {
        style.remove();
      }
    }
    return () => {
      document.body.classList.remove("dialog-open");
      const style = document.getElementById("mapbox-controls-hide");
      if (style) {
        style.remove();
      }
    };
  }, [open]);

  const handleSave = useCallback(() => {
    if (!name.trim()) {
      return;
    }

    // Use drawn geometry if available, otherwise use existing geometry or placeholder
    const geometry: GeoJSON.Feature = drawnGeometry || editingZone?.geometry || {
      type: "Feature",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [-122.42, 37.78],
            [-122.41, 37.78],
            [-122.41, 37.77],
            [-122.42, 37.77],
            [-122.42, 37.78],
          ],
        ],
      },
      properties: {},
    };

    const zoneData = {
      name: name.trim(),
      type,
      level,
      geometry,
      description: description.trim() || undefined,
    };

    if (editingZone && onUpdateZone) {
      onUpdateZone(editingZone.id, zoneData);
    } else {
      onCreateZone(zoneData);
    }

    // Reset form
    setName("");
    setType("fire_risk");
    setLevel("moderate");
    setDescription("");
    onOpenChange(false);
  }, [name, type, level, description, drawnGeometry, editingZone, onCreateZone, onUpdateZone, onOpenChange]);

  const getZoneTypeIcon = (zoneType: ZoneType) => {
    switch (zoneType) {
      case "fire_risk":
        return <AlertCircle className="h-4 w-4" />;
      case "psps":
        return <Zap className="h-4 w-4" />;
      case "irrigation":
        return <Droplet className="h-4 w-4" />;
      default:
        return <MapPin className="h-4 w-4" />;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{editingZone ? "Edit Risk Zone" : "Add New Risk Zone"}</DialogTitle>
          <DialogDescription>
            {editingZone
              ? "Update the zone details below. You can redraw the boundary if needed."
              : "Create a new risk zone on the map. Draw the zone boundary on the map, then fill in the details below."}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Drawing Mode Toggle */}
          {onToggleDrawing && (
            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
              <div>
                <Label className="text-sm font-medium text-blue-900">
                  Drawing Mode
                </Label>
                <p className="text-xs text-blue-700 mt-1">
                  {drawingMode
                    ? "Click on the map to draw the zone boundary"
                    : "Enable drawing mode to create a zone on the map"}
                </p>
              </div>
              <Button
                type="button"
                variant={drawingMode ? "default" : "outline"}
                size="sm"
                onClick={onToggleDrawing}
              >
                {drawingMode ? "Stop Drawing" : "Start Drawing"}
              </Button>
            </div>
          )}

          {/* Zone Name */}
          <div className="space-y-2">
            <Label htmlFor="zone-name">
              Zone Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="zone-name"
              placeholder="e.g., High Fire Risk Area A"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          {/* Zone Type */}
          <div className="space-y-2">
            <Label htmlFor="zone-type">Zone Type</Label>
            <Select value={type} onValueChange={(value) => setType(value as ZoneType)}>
              <SelectTrigger id="zone-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="fire_risk">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span>Fire Risk Zone</span>
                  </div>
                </SelectItem>
                <SelectItem value="psps">
                  <div className="flex items-center gap-2">
                    <Zap className="h-4 w-4 text-yellow-500" />
                    <span>PSPS Zone</span>
                  </div>
                </SelectItem>
                <SelectItem value="irrigation">
                  <div className="flex items-center gap-2">
                    <Droplet className="h-4 w-4 text-blue-500" />
                    <span>Irrigation Zone</span>
                  </div>
                </SelectItem>
                <SelectItem value="custom">
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-gray-500" />
                    <span>Custom Zone</span>
                  </div>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Risk Level */}
          <div className="space-y-2">
            <Label htmlFor="zone-level">Risk Level</Label>
            <Select value={level} onValueChange={(value) => setLevel(value as ZoneLevel)}>
              <SelectTrigger id="zone-level">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="critical">
                  <span className="text-red-600 font-medium">Critical</span>
                </SelectItem>
                <SelectItem value="high">
                  <span className="text-orange-600 font-medium">High</span>
                </SelectItem>
                <SelectItem value="moderate">
                  <span className="text-yellow-600 font-medium">Moderate</span>
                </SelectItem>
                <SelectItem value="low">
                  <span className="text-green-600 font-medium">Low</span>
                </SelectItem>
                <SelectItem value="info">
                  <span className="text-blue-600 font-medium">Info</span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="zone-description">Description (Optional)</Label>
            <Textarea
              id="zone-description"
              placeholder="Add notes about this zone..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          {/* Geometry Status */}
          {drawnGeometry ? (
            <div className="p-3 bg-green-50 rounded-lg border border-green-200">
              <p className="text-sm text-green-800">
                ✓ Zone boundary drawn on map
              </p>
            </div>
          ) : (
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-200">
              <p className="text-sm text-amber-800">
                ⚠ No zone boundary drawn. A default area will be used.
              </p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={!name.trim()}>
            {editingZone ? "Update Zone" : "Create Zone"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

