/**
 * Shared TypeScript type definitions for the Growgent frontend.
 *
 * This module contains common types and interfaces used across components.
 * Types match backend Pydantic schemas for consistency.
 * @module types
 */

/**
 * Standard API response wrapper from backend.
 * All backend endpoints return this format.
 */
export interface APIResponse<T = unknown> {
  status: "success" | "error";
  data: T;
  message?: string;
  errors?: string[] | null;
}

/**
 * Paginated response structure.
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * UUID type (string representation).
 */
export type UUID = string;

/**
 * Alert severity levels (matching backend enum).
 */
export type AlertSeverity = "critical" | "warning" | "info";

/**
 * Alert types (matching backend enum).
 */
export type AlertType = "irrigation" | "fire_risk" | "psps" | "sensor" | "weather" | "other";

/**
 * Agent types (matching backend enum).
 */
export type AgentType =
  | "fire_adaptive_irrigation"
  | "water_efficiency"
  | "psps_anticipation"
  | "fire_risk_reduction";

/**
 * Alert data structure (matching backend AlertResponse schema).
 */
export interface Alert {
  id: UUID;
  field_id: UUID | null;
  alert_type: AlertType;
  severity: AlertSeverity;
  message: string;
  agent_type: AgentType;
  acknowledged: boolean;
  acknowledged_at: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Paginated alert list response.
 */
export interface AlertListResponse {
  alerts: Alert[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Recommendation action types (matching backend enum).
 */
export type RecommendationAction = "irrigate" | "delay" | "pre_irrigate" | "skip";

/**
 * Recommendation data structure (matching backend RecommendationResponse schema).
 */
export interface Recommendation {
  id: UUID;
  field_id: UUID;
  agent_type: AgentType;
  action: RecommendationAction;
  title: string;
  reason: string;
  recommended_timing: string | null;
  zones_affected: string | null;
  confidence: number; // 0.0 to 1.0
  fire_risk_reduction_percent: number | null;
  water_saved_liters: number | null;
  psps_alert: boolean;
  accepted: boolean;
  accepted_at: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Paginated recommendation list response.
 */
export interface RecommendationListResponse {
  recommendations: Recommendation[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Field data structure (matching backend FieldResponse schema).
 */
export interface Field {
  id: UUID;
  farm_id: string;
  name: string;
  crop_type: string;
  area_hectares: number;
  location_geom: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Paginated field list response.
 */
export interface FieldListResponse {
  fields: Field[];
  total: number;
  page: number;
  page_size: number;
}

/**
 * Field detail response with sensor and fire risk data.
 */
export interface FieldDetailResponse {
  field: Field;
  latest_sensor_reading: {
    moisture_percent: number;
    temperature: number;
    ph: number;
    reading_timestamp: string;
  } | null;
  fire_risk_data: unknown | null;
}

/**
 * Water metrics response.
 */
export interface WaterMetrics {
  field_id: UUID;
  period: string;
  water_saved_liters: number;
  water_used_liters: number;
  efficiency_percent: number;
  recommendations_accepted: number;
  recommendations_total: number;
}

/**
 * Fire risk metrics response.
 */
export interface FireRiskMetrics {
  field_id: UUID;
  current_risk_level: string;
  risk_reduction_percent: number;
  recommendations_accepted: number;
  last_updated: string;
}

/**
 * Page navigation types.
 */
export type Page =
  | "dashboard"
  | "schedule"
  | "fields"
  | "fire-risk"
  | "metrics"
  | "alerts"
  | "chat"
  | "settings";

/**
 * Agent status types (for UI display).
 */
export type AgentStatus = "active" | "warning" | "error";

/**
 * Metric trend direction.
 */
export type TrendDirection = "up" | "down" | "neutral";

/**
 * Legacy recommendation format (for backward compatibility with existing components).
 * @deprecated Use Recommendation type instead
 */
export interface LegacyRecommendation {
  agent: string;
  title: string;
  confidence: number;
  reason: string;
  fields: string[];
  duration?: string;
  waterVolume?: string;
  fireRiskImpact?: string;
  waterSaved?: string;
}

/**
 * Risk zone types.
 */
export type ZoneType = "fire_risk" | "psps" | "irrigation" | "custom";

/**
 * Risk zone severity/level.
 */
export type ZoneLevel = "critical" | "high" | "moderate" | "low" | "info";

/**
 * Risk zone data structure.
 */
export interface RiskZone {
  id: UUID;
  name: string;
  type: ZoneType;
  level: ZoneLevel;
  geometry: GeoJSON.Feature; // GeoJSON Feature with Polygon/MultiPolygon geometry
  description?: string;
  created_at: string;
  updated_at: string;
}
