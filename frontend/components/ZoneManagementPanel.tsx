/**
 * ZoneManagementPanel component for managing risk zones.
 *
 * Provides:
 * - List of all zones
 * - Zone filtering by type and level
 * - Zone editing and deletion
 * - Zone export functionality
 *
 * @component
 */

import { useState, useMemo } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { AlertCircle, Zap, Droplet, MapPin, MoreVertical, Edit, Trash2, Download } from "lucide-react";
import type { RiskZone, ZoneType, ZoneLevel } from "../lib/types";
import { toast } from "sonner";

interface ZoneManagementPanelProps {
  /** All zones */
  zones: RiskZone[];
  /** Callback when zone should be edited */
  onEditZone: (zone: RiskZone) => void;
  /** Callback when zone should be deleted */
  onDeleteZone: (zoneId: string) => void;
  /** Filter state */
  filters: {
    types: ZoneType[];
    levels: ZoneLevel[];
  };
  /** Callback when filters change */
  onFiltersChange: (filters: { types: ZoneType[]; levels: ZoneLevel[] }) => void;
}

export function ZoneManagementPanel({
  zones,
  onEditZone,
  onDeleteZone,
  filters,
  onFiltersChange,
}: ZoneManagementPanelProps): JSX.Element {
  const [deleteZoneId, setDeleteZoneId] = useState<string | null>(null);

  // Filter zones based on active filters
  const filteredZones = useMemo(() => {
    return zones.filter((zone) => {
      const typeMatch = filters.types.length === 0 || filters.types.includes(zone.type);
      const levelMatch = filters.levels.length === 0 || filters.levels.includes(zone.level);
      return typeMatch && levelMatch;
    });
  }, [zones, filters]);

  const handleExportZones = () => {
    const geojson: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features: filteredZones.map((zone) => ({
        ...zone.geometry,
        properties: {
          id: zone.id,
          name: zone.name,
          type: zone.type,
          level: zone.level,
          description: zone.description,
          created_at: zone.created_at,
          updated_at: zone.updated_at,
        },
      })),
    };

    const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `zones-${new Date().toISOString().split("T")[0]}.geojson`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast.success(`Exported ${filteredZones.length} zone(s) as GeoJSON`);
  };

  const getZoneTypeIcon = (type: ZoneType) => {
    switch (type) {
      case "fire_risk":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case "psps":
        return <Zap className="h-4 w-4 text-yellow-500" />;
      case "irrigation":
        return <Droplet className="h-4 w-4 text-blue-500" />;
      default:
        return <MapPin className="h-4 w-4 text-gray-500" />;
    }
  };

  const getZoneLevelColor = (level: ZoneLevel) => {
    switch (level) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-300";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "moderate":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "low":
        return "bg-green-100 text-green-800 border-green-300";
      default:
        return "bg-blue-100 text-blue-800 border-blue-300";
    }
  };

  const handleToggleTypeFilter = (type: ZoneType) => {
    const newTypes = filters.types.includes(type)
      ? filters.types.filter((t) => t !== type)
      : [...filters.types, type];
    onFiltersChange({ ...filters, types: newTypes });
  };

  const handleToggleLevelFilter = (level: ZoneLevel) => {
    const newLevels = filters.levels.includes(level)
      ? filters.levels.filter((l) => l !== level)
      : [...filters.levels, level];
    onFiltersChange({ ...filters, levels: newLevels });
  };

  return (
    <>
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Zone Management</h3>
          <Button variant="outline" size="sm" onClick={handleExportZones} disabled={filteredZones.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Export ({filteredZones.length})
          </Button>
        </div>

        {/* Filters */}
        <div className="space-y-4 mb-6">
          <div>
            <Label className="text-sm font-medium mb-2 block">Filter by Type</Label>
            <div className="flex flex-wrap gap-3">
              {(["fire_risk", "psps", "irrigation", "custom"] as ZoneType[]).map((type) => (
                <div key={type} className="flex items-center space-x-2">
                  <Checkbox
                    id={`filter-type-${type}`}
                    checked={filters.types.includes(type)}
                    onCheckedChange={() => handleToggleTypeFilter(type)}
                  />
                  <Label
                    htmlFor={`filter-type-${type}`}
                    className="text-sm font-normal cursor-pointer flex items-center gap-1"
                  >
                    {getZoneTypeIcon(type)}
                    <span className="capitalize">{type.replace("_", " ")}</span>
                  </Label>
                </div>
              ))}
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium mb-2 block">Filter by Level</Label>
            <div className="flex flex-wrap gap-3">
              {(["critical", "high", "moderate", "low", "info"] as ZoneLevel[]).map((level) => (
                <div key={level} className="flex items-center space-x-2">
                  <Checkbox
                    id={`filter-level-${level}`}
                    checked={filters.levels.includes(level)}
                    onCheckedChange={() => handleToggleLevelFilter(level)}
                  />
                  <Label
                    htmlFor={`filter-level-${level}`}
                    className="text-sm font-normal cursor-pointer capitalize"
                  >
                    {level}
                  </Label>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Zone List */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {filteredZones.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-sm">
              {zones.length === 0 ? "No zones created yet" : "No zones match the current filters"}
            </div>
          ) : (
            filteredZones.map((zone) => (
              <div
                key={zone.id}
                className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200 hover:bg-slate-100 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {getZoneTypeIcon(zone.type)}
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-900 truncate">{zone.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className={`text-xs ${getZoneLevelColor(zone.level)}`}>
                        {zone.level}
                      </Badge>
                      <span className="text-xs text-slate-500 capitalize">{zone.type.replace("_", " ")}</span>
                    </div>
                  </div>
                </div>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => onEditZone(zone)}>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => setDeleteZoneId(zone.id)}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            ))
          )}
        </div>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteZoneId !== null} onOpenChange={(open) => !open && setDeleteZoneId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Zone</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this zone? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                if (deleteZoneId) {
                  onDeleteZone(deleteZoneId);
                  setDeleteZoneId(null);
                  toast.success("Zone deleted successfully");
                }
              }}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

