/**
 * FieldsMap component displays an interactive map of farm fields.
 *
 * Shows field boundaries, sensor data, NDVI, fire risk zones, and PSPS overlays.
 *
 * @component
 * @returns {JSX.Element} The fields map view
 */
import { useState, useCallback, useMemo, useEffect } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { Droplet, Thermometer, Activity, ChevronDown, ChevronUp } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";
import { MapboxMap } from "./MapboxMap";
import { AddZoneDialog } from "./AddZoneDialog";
import { ZoneManagementPanel } from "./ZoneManagementPanel";
import { useFields, useField } from "../lib/hooks/useFields";
import { Skeleton } from "./ui/skeleton";
import { toast } from "sonner";
import type { Field, RiskZone, ZoneType, ZoneLevel } from "../lib/types";

interface LayerState {
  /** Show satellite imagery layer */
  satellite: boolean;
  /** Show sensor locations layer */
  sensors: boolean;
  /** Show NDVI layer */
  ndvi: boolean;
  /** Show fire risk zones layer */
  fireRisk: boolean;
  /** Show PSPS zones layer */
  psps: boolean;
}

export function FieldsMap(): JSX.Element {
  const [layers, setLayers] = useState<LayerState>({
    satellite: true,
    sensors: true,
    ndvi: false,
    fireRisk: true,
    psps: true,
  });
  const [layersOpen, setLayersOpen] = useState(true);
  const [selectedFieldId, setSelectedFieldId] = useState<string | null>(null);
  
  // Zone management state
  const [zones, setZones] = useState<RiskZone[]>([]);
  const [addZoneDialogOpen, setAddZoneDialogOpen] = useState(false);
  const [editingZone, setEditingZone] = useState<RiskZone | null>(null);
  const [drawingMode, setDrawingMode] = useState(false);
  const [drawnGeometry, setDrawnGeometry] = useState<GeoJSON.Feature | null>(null);
  const [zoneFilters, setZoneFilters] = useState<{
    types: ZoneType[];
    levels: ZoneLevel[];
  }>({
    types: [],
    levels: [],
  });

  // Fetch fields data
  const { data: fieldsData, isLoading: isLoadingFields, error: fieldsError } = useFields();
  const fields = fieldsData?.fields || [];

  // Fetch selected field details
  const { data: fieldDetailData, isLoading: isLoadingFieldDetail } = useField(selectedFieldId);

  // Get selected field or first field as default
  const selectedField = useMemo(() => {
    if (fieldDetailData?.field) {
      const field = fieldDetailData.field as Field;
      const sensorReading = fieldDetailData.latest_sensor_reading;
      return {
        name: field.name,
        crop: field.crop_type,
        area: `${field.area_hectares} hectares`,
        ndvi: "0.68", // TODO: Get from sensor reading or NDVI data
        soilMoisture: sensorReading ? `${sensorReading.moisture_percent}%` : "N/A",
        sensors: 5, // TODO: Get actual sensor count from API
        fireRisk: "Low", // TODO: Get from fire_risk_data
        pspsStatus: "No shutoff predicted", // TODO: Get from PSPS data
      };
    }
    if (fields.length > 0 && !selectedFieldId) {
      // Auto-select first field if none selected
      const firstField = fields[0] as Field;
      return {
        name: firstField.name,
        crop: firstField.crop_type,
        area: `${firstField.area_hectares} hectares`,
        ndvi: "0.68",
        soilMoisture: "45%",
        sensors: 5,
        fireRisk: "Low",
        pspsStatus: "No shutoff predicted",
      };
    }
    return null;
  }, [fieldDetailData, fields, selectedFieldId]);

  // Auto-select first field on load
  useEffect(() => {
    if (fields.length > 0 && !selectedFieldId) {
      const firstField = fields[0] as Field;
      setSelectedFieldId(firstField.id);
    }
  }, [fields, selectedFieldId]);

  const handleFieldSelect = useCallback((fieldId: string) => {
    setSelectedFieldId(fieldId);
  }, []);

  const handleCreateZone = useCallback((zoneData: {
    name: string;
    type: ZoneType;
    level: ZoneLevel;
    geometry: GeoJSON.Feature;
    description?: string;
  }) => {
    const newZone: RiskZone = {
      id: crypto.randomUUID(),
      name: zoneData.name,
      type: zoneData.type,
      level: zoneData.level,
      geometry: zoneData.geometry,
      description: zoneData.description,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };

    setZones((prev) => [...prev, newZone]);
    setDrawingMode(false);
    setDrawnGeometry(null);
    toast.success(`Zone "${zoneData.name}" created successfully`);
  }, []);

  const handleUpdateZone = useCallback((zoneId: string, zoneData: {
    name: string;
    type: ZoneType;
    level: ZoneLevel;
    geometry: GeoJSON.Feature;
    description?: string;
  }) => {
    setZones((prev) =>
      prev.map((zone) =>
        zone.id === zoneId
          ? {
              ...zone,
              ...zoneData,
              updated_at: new Date().toISOString(),
            }
          : zone
      )
    );
    setEditingZone(null);
    setDrawingMode(false);
    setDrawnGeometry(null);
    toast.success(`Zone "${zoneData.name}" updated successfully`);
  }, []);

  const handleDeleteZone = useCallback((zoneId: string) => {
    setZones((prev) => prev.filter((zone) => zone.id !== zoneId));
  }, []);

  const handleEditZone = useCallback((zone: RiskZone) => {
    setEditingZone(zone);
    setAddZoneDialogOpen(true);
  }, []);

  // Filter zones based on active filters
  const filteredZones = useMemo(() => {
    return zones.filter((zone) => {
      const typeMatch = zoneFilters.types.length === 0 || zoneFilters.types.includes(zone.type);
      const levelMatch = zoneFilters.levels.length === 0 || zoneFilters.levels.includes(zone.level);
      return typeMatch && levelMatch;
    });
  }, [zones, zoneFilters]);

  const handleDrawingComplete = useCallback((geometry: GeoJSON.Feature) => {
    setDrawnGeometry(geometry);
    setDrawingMode(false);
    toast.success("Zone boundary drawn. Fill in the details to create the zone.");
  }, []);

  const handleToggleDrawing = useCallback(() => {
    setDrawingMode((prev) => !prev);
    if (drawingMode) {
      setDrawnGeometry(null);
    }
  }, [drawingMode]);

  const handleAddNewZone = useCallback(() => {
    setEditingZone(null);
    setDrawnGeometry(null);
    setAddZoneDialogOpen(true);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2>Field Map & Risk Zones</h2>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleAddNewZone}
          >
            Add New Zone
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => toast.info("Sensor management feature coming soon")}
          >
            Manage Sensors
          </Button>
        </div>
      </div>

      {/* Map Layer Controls - Moved to top */}
      <Card className="p-4">
        <Collapsible open={layersOpen} onOpenChange={setLayersOpen}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-700">Map Layers</h3>
            <CollapsibleTrigger asChild>
              <Button variant="ghost" size="sm">
                {layersOpen ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>
            </CollapsibleTrigger>
          </div>
          <CollapsibleContent className="pt-4">
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              <div className="flex items-center gap-2">
                <Switch
                  id="satellite"
                  checked={layers.satellite}
                  onCheckedChange={(checked) => setLayers({ ...layers, satellite: checked })}
                />
                <Label htmlFor="satellite" className="text-sm">Satellite</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="sensors"
                  checked={layers.sensors}
                  onCheckedChange={(checked) => setLayers({ ...layers, sensors: checked })}
                />
                <Label htmlFor="sensors" className="text-sm">Sensors</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="ndvi"
                  checked={layers.ndvi}
                  onCheckedChange={(checked) => setLayers({ ...layers, ndvi: checked })}
                />
                <Label htmlFor="ndvi" className="text-sm">NDVI</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="fireRisk"
                  checked={layers.fireRisk}
                  onCheckedChange={(checked) => setLayers({ ...layers, fireRisk: checked })}
                />
                <Label htmlFor="fireRisk" className="text-sm">Fire Risk</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="psps"
                  checked={layers.psps}
                  onCheckedChange={(checked) => setLayers({ ...layers, psps: checked })}
                />
                <Label htmlFor="psps" className="text-sm">PSPS Areas</Label>
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Area */}
        <div className="lg:col-span-2">
          <Card className="p-0 overflow-hidden relative">

            {/* Mapbox Map */}
            <div className="relative h-[600px]">
              {isLoadingFields ? (
                <div className="flex items-center justify-center h-full bg-slate-100">
                  <Skeleton className="w-full h-full" />
                </div>
              ) : fieldsError ? (
                <div className="flex items-center justify-center h-full bg-slate-100">
                  <div className="text-center p-8">
                    <p className="text-slate-700 mb-2">Failed to load fields</p>
                    <p className="text-sm text-slate-500">
                      {fieldsError instanceof Error ? fieldsError.message : "Unknown error"}
                    </p>
                  </div>
                </div>
              ) : fields.length === 0 ? (
                <div className="flex items-center justify-center h-full bg-slate-100">
                  <div className="text-center p-8">
                    <p className="text-slate-700 mb-2">No fields found</p>
                    <p className="text-sm text-slate-500">Add fields to see them on the map</p>
                  </div>
                </div>
                     ) : (
                       <MapboxMap
                         fields={fields as Field[]}
                         selectedFieldId={selectedFieldId}
                         onFieldSelect={handleFieldSelect}
                         layers={layers}
                         customZones={filteredZones.map((zone) => ({
                           id: zone.id,
                           name: zone.name,
                           type: zone.type,
                           level: zone.level,
                           geometry: zone.geometry,
                         }))}
                         drawingMode={drawingMode}
                         onDrawingComplete={handleDrawingComplete}
                       />
                     )}
            </div>
          </Card>
        </div>

        {/* Field Details Sidebar */}
        <div className="space-y-6">
          {/* Zone Management Panel */}
          <ZoneManagementPanel
            zones={zones}
            onEditZone={handleEditZone}
            onDeleteZone={handleDeleteZone}
            filters={zoneFilters}
            onFiltersChange={setZoneFilters}
          />

          {isLoadingFieldDetail || !selectedField ? (
            <Card className="p-6">
              <Skeleton className="h-6 w-32 mb-4" />
              <div className="space-y-4">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-20 w-full" />
              </div>
            </Card>
          ) : (
            <Card className="p-6">
              <h3 className="mb-4">{selectedField.name}</h3>

            <div className="space-y-4">
              <div>
                <p className="text-slate-600 mb-1">Crop Type</p>
                <p className="text-slate-900">{selectedField.crop}</p>
              </div>

              <div>
                <p className="text-slate-600 mb-1">Area</p>
                <p className="text-slate-900">{selectedField.area}</p>
              </div>

              <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                <Activity className="h-5 w-5 text-green-600" />
                <div>
                  <p className="text-slate-600">Current NDVI</p>
                  <p className="text-green-700">{selectedField.ndvi} (Good health)</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <Droplet className="h-5 w-5 text-blue-600" />
                <div>
                  <p className="text-slate-600">Soil Moisture</p>
                  <p className="text-blue-700">{selectedField.soilMoisture} (Optimal)</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 bg-emerald-50 rounded-lg">
                <Thermometer className="h-5 w-5 text-emerald-600" />
                <div>
                  <p className="text-slate-600">Active Sensors</p>
                  <p className="text-emerald-700">{selectedField.sensors} sensors</p>
                </div>
              </div>

              <div>
                <p className="text-slate-600 mb-1">Fire Risk Level</p>
                <Badge variant="outline" className="text-green-600 border-green-600">
                  {selectedField.fireRisk}
                </Badge>
              </div>

              <div>
                <p className="text-slate-600 mb-1">PSPS Status</p>
                <p className="text-slate-900">{selectedField.pspsStatus}</p>
              </div>
            </div>

            <div className="mt-6">
              <Button 
                className="w-full bg-emerald-600 hover:bg-emerald-700"
                onClick={() => toast.info("Viewing recommendations for " + selectedField.name)}
              >
                View Recommendations
              </Button>
            </div>
            </Card>
          )}
          
          <Card className="p-6">
            <h4 className="mb-4">Recent Activity</h4>
            <div className="space-y-3">
              <div className="p-3 bg-slate-50 rounded-lg">
                <p className="text-slate-700 mb-1">Irrigation completed</p>
                <p className="text-slate-500">2 hours ago</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <p className="text-slate-700 mb-1">NDVI reading updated</p>
                <p className="text-slate-500">5 hours ago</p>
              </div>
              <div className="p-3 bg-slate-50 rounded-lg">
                <p className="text-slate-700 mb-1">Sensor maintenance</p>
                <p className="text-slate-500">1 day ago</p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Add/Edit Zone Dialog */}
      <AddZoneDialog
        open={addZoneDialogOpen}
        onOpenChange={(open) => {
          setAddZoneDialogOpen(open);
          if (!open) {
            setEditingZone(null);
            setDrawnGeometry(null);
          }
        }}
        onCreateZone={handleCreateZone}
        onUpdateZone={handleUpdateZone}
        editingZone={editingZone}
        drawingMode={drawingMode}
        onToggleDrawing={handleToggleDrawing}
        drawnGeometry={drawnGeometry}
      />
    </div>
  );
}
