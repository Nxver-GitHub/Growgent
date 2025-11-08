/**
 * Application constants for Growgent frontend.
 *
 * Contains API endpoints, routes, colors, and other configuration values.
 * @module constants
 */

/**
 * API endpoint base URL.
 * In production, this should be set via environment variable.
 * 
 * Defaults to http://localhost:8000 for local Docker backend.
 * Set VITE_API_BASE_URL in .env.local to override.
 */
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Mapbox access token for GIS map visualization.
 * Set VITE_MAPBOX_TOKEN in .env.local
 */
export const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || "";

/**
 * API endpoint paths.
 * These endpoints are provided by Agent 1 (Backend Architect) and Agent 2 (Data Intelligence).
 */
export const API_ENDPOINTS = {
  /** Dashboard consolidated data (Agent 1) */
  DASHBOARD: "/api/dashboard",
  /** Irrigation recommendations (Agent 1) */
  IRRIGATION_RECOMMENDATIONS: "/api/agents/irrigation/recommendations",
  /** Fields with geometry (Agent 1) */
  FIELDS: "/api/fields",
  /** Fire risk data (Agent 1) */
  FIRE_RISK: "/api/fire-risk",
  /** Alerts (Agent 2) */
  ALERTS: "/api/alerts",
  /** Water metrics (Agent 2) */
  METRICS_WATER: "/api/metrics/water",
  /** Fire risk metrics (Agent 2) */
  METRICS_FIRE_RISK: "/api/metrics/fire-risk",
  /** Chat endpoint (Agent 1) */
  CHAT: "/api/agents/chat",
} as const;

/**
 * Application routes.
 */
export const ROUTES = {
  DASHBOARD: "dashboard",
  SCHEDULE: "schedule",
  FIELDS: "fields",
  FIRE_RISK: "fire-risk",
  METRICS: "metrics",
  ALERTS: "alerts",
  CHAT: "chat",
  SETTINGS: "settings",
} as const;

/**
 * Design system colors (from Agent 3 prompt).
 */
export const COLORS = {
  EMERALD: "#10B981",
  SKY_BLUE: "#0EA5E9",
  AMBER: "#F59E0B",
  RED: "#EF4444",
  GREEN: "#22C55E",
} as const;

/**
 * Spacing units (8px base).
 */
export const SPACING = {
  XS: "8px",
  SM: "16px",
  MD: "24px",
  LG: "32px",
  XL: "40px",
} as const;

/**
 * Border radius values.
 */
export const BORDER_RADIUS = {
  DEFAULT: "8px",
  CARD: "12px",
  LARGE: "16px",
} as const;

/**
 * React Query configuration.
 */
export const QUERY_CONFIG = {
  /** Default stale time for queries (5 minutes) */
  STALE_TIME: 5 * 60 * 1000,
  /** Default cache time (10 minutes) */
  CACHE_TIME: 10 * 60 * 1000,
  /** Retry attempts for failed queries */
  RETRY: 3,
  /** Retry delay in milliseconds */
  RETRY_DELAY: 1000,
} as const;

/**
 * Pagination defaults.
 */
export const PAGINATION = {
  /** Default page size for alerts */
  ALERTS_PAGE_SIZE: 20,
  /** Maximum page size */
  MAX_PAGE_SIZE: 100,
} as const;

/**
 * Polling intervals (in milliseconds).
 */
export const POLLING_INTERVALS = {
  /** Alerts polling interval (30 seconds) */
  ALERTS: 30 * 1000,
  /** Dashboard data polling interval (5 minutes) */
  DASHBOARD: 5 * 60 * 1000,
  /** Fire risk zones polling interval (5 minutes) */
  FIRE_RISK: 5 * 60 * 1000,
} as const;

