/**
 * MapboxMap component provides the core Mapbox GL JS map integration.
 *
 * Handles map initialization, layer management, and field selection.
 *
 * @component
 */

import { useEffect, useRef, useState, useCallback } from "react";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import { MAPBOX_TOKEN } from "../lib/constants";
import type { Field } from "../lib/types";

interface MapboxMapProps {
  /** Fields data to display on map */
  fields: Field[];
  /** Selected field ID */
  selectedFieldId: string | null;
  /** Callback when field is selected */
  onFieldSelect: (fieldId: string) => void;
  /** Layer visibility state */
  layers: {
    satellite: boolean;
    sensors: boolean;
    ndvi: boolean;
    fireRisk: boolean;
    psps: boolean;
  };
  /** Custom risk zones to display */
  customZones?: Array<{
    id: string;
    name: string;
    type: "fire_risk" | "psps" | "irrigation" | "custom";
    level: "critical" | "high" | "moderate" | "low" | "info";
    geometry: GeoJSON.Feature;
  }>;
  /** Whether drawing mode is active */
  drawingMode?: boolean;
  /** Callback when drawing is complete */
  onDrawingComplete?: (geometry: GeoJSON.Feature) => void;
}

export function MapboxMap({
  fields,
  selectedFieldId,
  onFieldSelect,
  layers,
  customZones = [],
  drawingMode = false,
  onDrawingComplete,
}: MapboxMapProps): JSX.Element {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  
  // Drawing state
  const drawingPointsRef = useRef<[number, number][]>([]);
  const drawingMarkersRef = useRef<mapboxgl.Marker[]>([]);
  const drawingSourceId = "drawing-source";
  const drawingLineLayerId = "drawing-line";

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    if (!MAPBOX_TOKEN) {
      console.error("❌ Mapbox token not found. Please set VITE_MAPBOX_TOKEN in .env.local");
      return;
    }

    try {
      mapboxgl.accessToken = MAPBOX_TOKEN;

      console.log("🗺️ Initializing Mapbox map...");

      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: layers.satellite
          ? "mapbox://styles/mapbox/satellite-v9"
          : "mapbox://styles/mapbox/light-v11",
        center: [-122.4194, 37.7749], // Default to San Francisco area (adjust to your farm location)
        zoom: 12,
        attributionControl: false,
      });

      map.current.addControl(new mapboxgl.NavigationControl(), "top-right");
      map.current.addControl(new mapboxgl.FullscreenControl(), "top-right");

      map.current.on("load", () => {
        console.log("✅ Mapbox map loaded successfully");
        setMapLoaded(true);
      });

      map.current.on("error", (e) => {
        console.error("❌ Mapbox error:", e);
      });

      return () => {
        if (map.current) {
          map.current.remove();
          map.current = null;
        }
      };
    } catch (error) {
      console.error("❌ Failed to initialize Mapbox map:", error);
    }
  }, []);

  // Update map style when satellite layer toggles
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    const style = layers.satellite
      ? "mapbox://styles/mapbox/satellite-v9"
      : "mapbox://styles/mapbox/light-v11";

    map.current.setStyle(style);
  }, [layers.satellite, mapLoaded]);

  // Parse GeoJSON from location_geom string
  const parseFieldGeometry = useCallback((geomString: string | null): GeoJSON.Feature | null => {
    if (!geomString) return null;

    try {
      // Try parsing as GeoJSON string
      const parsed = typeof geomString === "string" ? JSON.parse(geomString) : geomString;
      
      // If it's already a Feature, return it
      if (parsed.type === "Feature") {
        return parsed as GeoJSON.Feature;
      }

      // If it's a Geometry, wrap it in a Feature
      if (parsed.type && ["Point", "LineString", "Polygon", "MultiPolygon"].includes(parsed.type)) {
        return {
          type: "Feature",
          geometry: parsed as GeoJSON.Geometry,
          properties: {},
        };
      }

      return null;
    } catch (error) {
      console.warn("Failed to parse field geometry:", error);
      return null;
    }
  }, []);

  // Add/update field boundaries layer
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    const sourceId = "fields-source";
    const layerId = "fields-layer";
    const outlineLayerId = "fields-outline";

    // Create GeoJSON from fields
    const features: GeoJSON.Feature[] = fields
      .map((field) => {
        const feature = parseFieldGeometry(field.location_geom);
        if (feature) {
          return {
            ...feature,
            properties: {
              id: field.id,
              name: field.name,
              crop_type: field.crop_type,
              area_hectares: field.area_hectares,
            },
          };
        }
        return null;
      })
      .filter((f): f is GeoJSON.Feature => f !== null);

    const geoJson: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features,
    };

    // Remove existing layers and source if they exist
    if (map.current.getLayer(layerId)) {
      map.current.removeLayer(layerId);
    }
    if (map.current.getLayer(outlineLayerId)) {
      map.current.removeLayer(outlineLayerId);
    }
    if (map.current.getSource(sourceId)) {
      map.current.removeSource(sourceId);
    }

    // Add source and layers
    if (features.length > 0) {
      map.current.addSource(sourceId, {
        type: "geojson",
        data: geoJson,
      });

      // Add fill layer
      map.current.addLayer({
        id: layerId,
        type: "fill",
        source: sourceId,
        paint: {
          "fill-color": [
            "case",
            ["==", ["get", "id"], selectedFieldId || ""],
            "#10B981", // emerald-500 for selected
            "#34D399", // emerald-400 for unselected
          ],
          "fill-opacity": 0.3,
        },
      });

      // Add outline layer
      map.current.addLayer({
        id: outlineLayerId,
        type: "line",
        source: sourceId,
        paint: {
          "line-color": [
            "case",
            ["==", ["get", "id"], selectedFieldId || ""],
            "#10B981", // emerald-500 for selected
            "#6EE7B7", // emerald-300 for unselected
          ],
          "line-width": 2,
          "line-opacity": 0.8,
        },
      });

      // Add click handler for field selection
      map.current.on("click", layerId, (e) => {
        if (e.features && e.features[0] && e.features[0].properties) {
          const fieldId = e.features[0].properties.id as string;
          if (fieldId) {
            onFieldSelect(fieldId);
          }
        }
      });

      // Change cursor on hover
      map.current.on("mouseenter", layerId, () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = "pointer";
        }
      });

      map.current.on("mouseleave", layerId, () => {
        if (map.current) {
          map.current.getCanvas().style.cursor = "";
        }
      });
    }

    return () => {
      if (map.current) {
        map.current.off("click", layerId);
        map.current.off("mouseenter", layerId);
        map.current.off("mouseleave", layerId);
      }
    };
  }, [fields, selectedFieldId, mapLoaded, parseFieldGeometry, onFieldSelect]);

  // Add fire risk zones layer (placeholder - would need actual fire risk GeoJSON from API)
  useEffect(() => {
    if (!map.current || !mapLoaded || !layers.fireRisk) return;

    const sourceId = "fire-risk-source";
    const layerId = "fire-risk-layer";

    // Remove existing layer if it exists
    if (map.current.getLayer(layerId)) {
      map.current.removeLayer(layerId);
    }
    if (map.current.getSource(sourceId)) {
      map.current.removeSource(sourceId);
    }

    // TODO: Fetch actual fire risk zones from API
    // For now, create a placeholder zone around fields
    const fireRiskFeatures: GeoJSON.Feature[] = fields
      .map((field) => {
        const feature = parseFieldGeometry(field.location_geom);
        if (feature && feature.geometry.type === "Polygon") {
          // Create a buffer zone (simplified - in production, use turf.js for proper buffering)
          return {
            type: "Feature" as const,
            geometry: feature.geometry,
            properties: {
              risk_level: "moderate",
              field_id: field.id,
            },
          };
        }
        return null;
      })
      .filter((f): f is GeoJSON.Feature => f !== null);

    if (fireRiskFeatures.length > 0) {
      map.current.addSource(sourceId, {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: fireRiskFeatures,
        },
      });

      map.current.addLayer({
        id: layerId,
        type: "fill",
        source: sourceId,
        paint: {
          "fill-color": [
            "case",
            ["==", ["get", "risk_level"], "high"],
            "#EF4444", // red-500
            ["==", ["get", "risk_level"], "moderate"],
            "#F59E0B", // amber-500
            "#FCD34D", // amber-300
          ],
          "fill-opacity": 0.2,
        },
      });
    }

    return () => {
      if (map.current && map.current.getLayer(layerId)) {
        map.current.removeLayer(layerId);
      }
      if (map.current && map.current.getSource(sourceId)) {
        map.current.removeSource(sourceId);
      }
    };
  }, [fields, layers.fireRisk, mapLoaded, parseFieldGeometry]);

  // Add PSPS zones layer (placeholder)
  useEffect(() => {
    if (!map.current || !mapLoaded || !layers.psps) return;

    const sourceId = "psps-source";
    const layerId = "psps-layer";

    // Remove existing layer if it exists
    if (map.current.getLayer(layerId)) {
      map.current.removeLayer(layerId);
    }
    if (map.current.getSource(sourceId)) {
      map.current.removeSource(sourceId);
    }

    // TODO: Fetch actual PSPS zones from API
    // For now, create placeholder zones
    const pspsFeatures: GeoJSON.Feature[] = [];

    if (pspsFeatures.length > 0) {
      map.current.addSource(sourceId, {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: pspsFeatures,
        },
      });

      map.current.addLayer({
        id: layerId,
        type: "fill",
        source: sourceId,
        paint: {
          "fill-color": "#A855F7", // purple-500
          "fill-opacity": 0.3,
        },
      });

      map.current.addLayer({
        id: `${layerId}-outline`,
        type: "line",
        source: sourceId,
        paint: {
          "line-color": "#A855F7",
          "line-width": 2,
          "line-dasharray": [2, 2],
        },
      });
    }

    return () => {
      if (map.current && map.current.getLayer(layerId)) {
        map.current.removeLayer(layerId);
      }
      if (map.current && map.current.getLayer(`${layerId}-outline`)) {
        map.current.removeLayer(`${layerId}-outline`);
      }
      if (map.current && map.current.getSource(sourceId)) {
        map.current.removeSource(sourceId);
      }
    };
  }, [layers.psps, mapLoaded]);

  // Add sensor markers (placeholder - would need sensor locations from API)
  useEffect(() => {
    if (!map.current || !mapLoaded || !layers.sensors) return;

    // TODO: Fetch actual sensor locations from API
    // For now, create placeholder markers on field centroids
    const markers: mapboxgl.Marker[] = [];

    fields.forEach((field) => {
      const feature = parseFieldGeometry(field.location_geom);
      if (feature && feature.geometry.type === "Polygon") {
        // Calculate centroid (simplified - in production, use turf.js)
        const coordinates = feature.geometry.coordinates[0];
        const lng = coordinates.reduce((sum, coord) => sum + coord[0], 0) / coordinates.length;
        const lat = coordinates.reduce((sum, coord) => sum + coord[1], 0) / coordinates.length;

        const el = document.createElement("div");
        el.className = "sensor-marker";
        el.style.width = "12px";
        el.style.height = "12px";
        el.style.borderRadius = "50%";
        el.style.backgroundColor = "#3B82F6"; // blue-500
        el.style.border = "2px solid white";
        el.style.boxShadow = "0 2px 4px rgba(0,0,0,0.3)";
        el.style.cursor = "pointer";

        const marker = new mapboxgl.Marker(el)
          .setLngLat([lng, lat])
          .setPopup(
            new mapboxgl.Popup({ offset: 25 }).setHTML(
              `<div class="p-2">
                <p class="font-semibold">Sensor</p>
                <p class="text-sm text-slate-600">Field: ${field.name}</p>
              </div>`
            )
          )
          .addTo(map.current!);

        markers.push(marker);
      }
    });

    return () => {
      markers.forEach((marker) => marker.remove());
    };
  }, [fields, layers.sensors, mapLoaded, parseFieldGeometry]);

  // Drawing mode handler
  useEffect(() => {
    if (!map.current || !mapLoaded) return;

    const handleMapClick = (e: mapboxgl.MapMouseEvent) => {
      if (!drawingMode) return;

      const { lng, lat } = e.lngLat;
      drawingPointsRef.current.push([lng, lat]);

      // Add marker for the point
      const el = document.createElement("div");
      el.className = "drawing-point";
      el.style.width = "10px";
      el.style.height = "10px";
      el.style.borderRadius = "50%";
      el.style.backgroundColor = "#EF4444";
      el.style.border = "2px solid white";
      el.style.boxShadow = "0 2px 4px rgba(0,0,0,0.3)";
      el.style.cursor = "pointer";

      const marker = new mapboxgl.Marker(el).setLngLat([lng, lat]).addTo(map.current!);
      drawingMarkersRef.current.push(marker);

      // Update line if we have at least 2 points
      if (drawingPointsRef.current.length >= 2) {
        const lineCoordinates = [...drawingPointsRef.current];
        // Close the polygon by adding the first point at the end if we have 3+ points
        if (drawingPointsRef.current.length >= 3) {
          lineCoordinates.push(drawingPointsRef.current[0]);
        }

        const lineFeature: GeoJSON.Feature = {
          type: "Feature",
          geometry: {
            type: "LineString",
            coordinates: lineCoordinates,
          },
          properties: {},
        };

        // Update or create the drawing line source
        if (map.current.getSource(drawingSourceId)) {
          (map.current.getSource(drawingSourceId) as mapboxgl.GeoJSONSource).setData({
            type: "FeatureCollection",
            features: [lineFeature],
          });
        } else {
          map.current.addSource(drawingSourceId, {
            type: "geojson",
            data: {
              type: "FeatureCollection",
              features: [lineFeature],
            },
          });

          if (!map.current.getLayer(drawingLineLayerId)) {
            map.current.addLayer({
              id: drawingLineLayerId,
              type: "line",
              source: drawingSourceId,
              paint: {
                "line-color": "#EF4444",
                "line-width": 2,
                "line-dasharray": [2, 2],
              },
            });
          }
        }
      }
    };

    const handleMapDblClick = (e: mapboxgl.MapMouseEvent) => {
      if (!drawingMode || drawingPointsRef.current.length < 3) return;

      e.preventDefault();

      // Complete the polygon
      const coordinates = [...drawingPointsRef.current, drawingPointsRef.current[0]];

      const geometry: GeoJSON.Feature = {
        type: "Feature",
        geometry: {
          type: "Polygon",
          coordinates: [coordinates],
        },
        properties: {},
      };

      if (onDrawingComplete) {
        onDrawingComplete(geometry);
      }

      // Clear drawing
      drawingPointsRef.current = [];
      drawingMarkersRef.current.forEach((marker) => marker.remove());
      drawingMarkersRef.current = [];
      if (map.current.getLayer(drawingLineLayerId)) {
        map.current.removeLayer(drawingLineLayerId);
      }
      if (map.current.getSource(drawingSourceId)) {
        map.current.removeSource(drawingSourceId);
      }
    };

    if (drawingMode) {
      map.current.on("click", handleMapClick);
      map.current.on("dblclick", handleMapDblClick);
      map.current.getCanvas().style.cursor = "crosshair";
    } else {
      map.current.off("click", handleMapClick);
      map.current.off("dblclick", handleMapDblClick);
      map.current.getCanvas().style.cursor = "";
      
      // Clear drawing when mode is disabled
      drawingPointsRef.current = [];
      drawingMarkersRef.current.forEach((marker) => marker.remove());
      drawingMarkersRef.current = [];
      if (map.current.getLayer(drawingLineLayerId)) {
        map.current.removeLayer(drawingLineLayerId);
      }
      if (map.current.getSource(drawingSourceId)) {
        map.current.removeSource(drawingSourceId);
      }
    }

    return () => {
      if (map.current) {
        map.current.off("click", handleMapClick);
        map.current.off("dblclick", handleMapDblClick);
      }
    };
  }, [drawingMode, mapLoaded, onDrawingComplete]);

  // Display custom zones
  useEffect(() => {
    if (!map.current || !mapLoaded || customZones.length === 0) return;

    const sourceId = "custom-zones-source";
    const layerId = "custom-zones-layer";
    const outlineLayerId = "custom-zones-outline";

    // Remove existing layers if they exist
    if (map.current.getLayer(layerId)) {
      map.current.removeLayer(layerId);
    }
    if (map.current.getLayer(outlineLayerId)) {
      map.current.removeLayer(outlineLayerId);
    }
    if (map.current.getSource(sourceId)) {
      map.current.removeSource(sourceId);
    }

    // Create GeoJSON from custom zones
    const features: GeoJSON.Feature[] = customZones.map((zone) => ({
      ...zone.geometry,
      properties: {
        id: zone.id,
        name: zone.name,
        type: zone.type,
        level: zone.level,
      },
    }));

    const geojson: GeoJSON.FeatureCollection = {
      type: "FeatureCollection",
      features,
    };

    map.current.addSource(sourceId, {
      type: "geojson",
      data: geojson,
    });

    // Add fill layer
    map.current.addLayer({
      id: layerId,
      type: "fill",
      source: sourceId,
      paint: {
        "fill-color": [
          "match",
          ["get", "level"],
          "critical",
          "#DC2626", // red-600
          "high",
          "#EA580C", // orange-600
          "moderate",
          "#F59E0B", // amber-500
          "low",
          "#10B981", // emerald-500
          "#3B82F6", // blue-500 (info)
        ],
        "fill-opacity": 0.3,
      },
    });

    // Add outline layer
    map.current.addLayer({
      id: outlineLayerId,
      type: "line",
      source: sourceId,
      paint: {
        "line-color": [
          "match",
          ["get", "level"],
          "critical",
          "#991B1B", // red-800
          "high",
          "#C2410C", // orange-800
          "moderate",
          "#D97706", // amber-600
          "low",
          "#059669", // emerald-600
          "#1E40AF", // blue-800 (info)
        ],
        "line-width": 2,
        "line-dasharray": [2, 2],
      },
    });

    // Add click handler for zones
    map.current.on("click", layerId, (e) => {
      if (e.features && e.features.length > 0) {
        const feature = e.features[0];
        const props = feature?.properties;
        if (props) {
          new mapboxgl.Popup()
            .setLngLat(e.lngLat)
            .setHTML(
              `<div class="p-2">
                <h3 class="font-semibold">${props.name || "Zone"}</h3>
                <p class="text-sm text-slate-600">Type: ${props.type || "Unknown"}</p>
                <p class="text-sm text-slate-600">Level: ${props.level || "Unknown"}</p>
              </div>`
            )
            .addTo(map.current!);
        }
      }
    });

    // Change cursor on hover
    map.current.on("mouseenter", layerId, () => {
      if (map.current) map.current.getCanvas().style.cursor = "pointer";
    });
    map.current.on("mouseleave", layerId, () => {
      if (map.current) map.current.getCanvas().style.cursor = "";
    });

    return () => {
      if (map.current) {
        if (map.current.getLayer(layerId)) map.current.removeLayer(layerId);
        if (map.current.getLayer(outlineLayerId)) map.current.removeLayer(outlineLayerId);
        if (map.current.getSource(sourceId)) map.current.removeSource(sourceId);
        map.current.off("click", layerId);
        map.current.off("mouseenter", layerId);
        map.current.off("mouseleave", layerId);
      }
    };
  }, [customZones, mapLoaded]);

  // NDVI heatmap layer (placeholder - would need NDVI raster data)
  useEffect(() => {
    if (!map.current || !mapLoaded || !layers.ndvi) return;

    // TODO: Add NDVI heatmap layer using Mapbox raster source
    // This would require NDVI data as a raster tile service
    // For now, we'll skip this as it requires backend raster generation

    return () => {
      // Cleanup if needed
    };
  }, [layers.ndvi, mapLoaded]);

  // Debug: Log token status (only in development)
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      console.log("🗺️ Mapbox Debug:", {
        hasToken: !!MAPBOX_TOKEN,
        tokenLength: MAPBOX_TOKEN?.length || 0,
        tokenPrefix: MAPBOX_TOKEN?.substring(0, 10) || "none",
        envVar: import.meta.env.VITE_MAPBOX_TOKEN ? "found" : "missing",
      });
    }
  }, []);

  if (!MAPBOX_TOKEN) {
    return (
      <div className="flex items-center justify-center h-full bg-slate-100 rounded-lg">
        <div className="text-center p-8">
          <p className="text-slate-700 mb-2 font-semibold">Mapbox token not configured</p>
          <p className="text-sm text-slate-500 mb-4">
            Please set VITE_MAPBOX_TOKEN in your .env.local file
          </p>
          <div className="text-xs text-slate-400 mt-4 p-3 bg-slate-50 rounded">
            <p>Debug info:</p>
            <p>• Env var loaded: {import.meta.env.VITE_MAPBOX_TOKEN ? "Yes" : "No"}</p>
            <p>• Token length: {MAPBOX_TOKEN?.length || 0}</p>
            <p className="mt-2 text-amber-600">
              ⚠️ Make sure to restart the Vite dev server after adding the token!
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={mapContainer} 
      className="w-full h-full relative mapbox-container" 
      style={{ minHeight: "600px", isolation: "isolate" }} 
    />
  );
}

