import { useState } from "react";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Label } from "./ui/label";
import { MapPin, Droplet, Thermometer, Activity, ChevronDown, ChevronUp } from "lucide-react";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "./ui/collapsible";

export function FieldsMap() {
  const [layers, setLayers] = useState({
    satellite: true,
    sensors: true,
    ndvi: false,
    fireRisk: true,
    psps: true,
  });
  const [layersOpen, setLayersOpen] = useState(true);

  const selectedField = {
    name: "Field 1 North",
    crop: "Strawberry",
    area: "12 hectares",
    ndvi: "0.68",
    soilMoisture: "45%",
    sensors: 5,
    fireRisk: "Low",
    pspsStatus: "No shutoff predicted",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2>Field Map & Risk Zones</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            Add New Zone
          </Button>
          <Button variant="outline" size="sm">
            Manage Sensors
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Area */}
        <div className="lg:col-span-2">
          <Card className="p-0 overflow-hidden">
            {/* Map Controls - Collapsible */}
            <Collapsible
              open={layersOpen}
              onOpenChange={setLayersOpen}
              className="absolute top-4 left-4 z-10"
            >
              <div className="bg-white rounded-lg shadow-lg">
                <CollapsibleTrigger asChild>
                  <Button
                    variant="ghost"
                    className="w-full justify-between p-4"
                  >
                    <span>Map Layers</span>
                    {layersOpen ? (
                      <ChevronUp className="h-4 w-4" />
                    ) : (
                      <ChevronDown className="h-4 w-4" />
                    )}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent className="p-4 pt-0 space-y-3">
                  <div className="flex items-center gap-2">
                    <Switch
                      id="satellite"
                      checked={layers.satellite}
                      onCheckedChange={(checked) =>
                        setLayers({ ...layers, satellite: checked })
                      }
                    />
                    <Label htmlFor="satellite">Satellite Imagery</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="sensors"
                      checked={layers.sensors}
                      onCheckedChange={(checked) =>
                        setLayers({ ...layers, sensors: checked })
                      }
                    />
                    <Label htmlFor="sensors">Sensors</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="ndvi"
                      checked={layers.ndvi}
                      onCheckedChange={(checked) =>
                        setLayers({ ...layers, ndvi: checked })
                      }
                    />
                    <Label htmlFor="ndvi">NDVI Heatmap</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="fireRisk"
                      checked={layers.fireRisk}
                      onCheckedChange={(checked) =>
                        setLayers({ ...layers, fireRisk: checked })
                      }
                    />
                    <Label htmlFor="fireRisk">Fire Risk Zones</Label>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      id="psps"
                      checked={layers.psps}
                      onCheckedChange={(checked) =>
                        setLayers({ ...layers, psps: checked })
                      }
                    />
                    <Label htmlFor="psps">PSPS Areas</Label>
                  </div>
                </CollapsibleContent>
              </div>
            </Collapsible>

            {/* Map Placeholder */}
            <div className="relative h-[600px] bg-gradient-to-br from-emerald-100 to-sky-100 flex items-center justify-center">
              <div className="text-center space-y-4">
                <MapPin className="h-16 w-16 text-emerald-600 mx-auto" />
                <div>
                  <p className="text-slate-700">Interactive Map View</p>
                  <p className="text-slate-500">
                    Mapbox integration displays fields, sensors, and risk zones
                  </p>
                </div>
              </div>

              {/* Sample Field Boundaries */}
              <div className="absolute top-32 left-32 w-48 h-40 border-4 border-emerald-500 rounded-lg bg-emerald-500 bg-opacity-20">
                <div className="absolute -top-8 left-4">
                  <Badge className="bg-emerald-600">Field 1</Badge>
                </div>
              </div>

              <div className="absolute top-48 right-48 w-56 h-48 border-4 border-emerald-500 rounded-lg bg-emerald-500 bg-opacity-20">
                <div className="absolute -top-8 left-4">
                  <Badge className="bg-emerald-600">Field 2</Badge>
                </div>
              </div>

              {/* Sample Sensor Markers */}
              <div className="absolute top-40 left-40 w-6 h-6 bg-blue-500 rounded-full border-2 border-white shadow-lg" />
              <div className="absolute top-56 left-56 w-6 h-6 bg-blue-500 rounded-full border-2 border-white shadow-lg" />
              <div className="absolute top-60 right-56 w-6 h-6 bg-blue-500 rounded-full border-2 border-white shadow-lg" />
            </div>
          </Card>
        </div>

        {/* Field Details Sidebar */}
        <div className="space-y-6">
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
              <Button className="w-full bg-emerald-600 hover:bg-emerald-700">
                View Recommendations
              </Button>
            </div>
          </Card>

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
    </div>
  );
}
