/**
 * API client for Growgent frontend.
 *
 * Provides React Query setup and fetch functions for backend API integration.
 * All endpoints are provided by Agent 1 (Backend Architect) and Agent 2 (Data Intelligence).
 *
 * @module api
 */

import { QueryClient } from "@tanstack/react-query";
import { API_BASE_URL, API_ENDPOINTS, QUERY_CONFIG } from "./constants";
import type { APIResponse } from "./types";

/**
 * React Query client instance.
 *
 * Configured with default options for caching, retries, and stale time.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: QUERY_CONFIG.STALE_TIME,
      gcTime: QUERY_CONFIG.CACHE_TIME,
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors (client errors)
        if (error instanceof Error && error.message.includes("40")) {
          return false;
        }
        return failureCount < QUERY_CONFIG.RETRY;
      },
      retryDelay: QUERY_CONFIG.RETRY_DELAY,
      refetchOnWindowFocus: false,
      networkMode: "online",
    },
  },
});

/**
 * Base fetch function with error handling.
 * Handles the APIResponse wrapper format from backend.
 *
 * @param endpoint - API endpoint path
 * @param options - Fetch options
 * @returns Promise resolving to unwrapped data from APIResponse
 * @throws Error if request fails
 */
/**
 * Create an AbortController with timeout.
 */
function createTimeoutController(timeoutMs = 10000): AbortController {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeoutMs);
  return controller;
}

async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Add timeout (10 seconds default)
  const timeoutController = createTimeoutController(10000);
  // Use provided signal or timeout signal
  const signal = options?.signal || timeoutController.signal;
  
  try {
    const response = await fetch(url, {
      ...options,
      signal,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      // Try to parse error response
      let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch {
        // If error response is not JSON, use default message
      }
      throw new Error(errorMessage);
    }

    const apiResponse = await response.json() as APIResponse<T>;
    
    // Check if response has error status
    if (apiResponse.status === "error") {
      const errorMsg = apiResponse.message || "An error occurred";
      throw new Error(errorMsg);
    }

    // Return unwrapped data
    return apiResponse.data;
  } catch (error) {
    if (error instanceof Error) {
      // Handle timeout specifically
      if (error.name === "AbortError" || error.message.includes("aborted")) {
        throw new Error("Request timed out. Please check your connection and try again.");
      }
      throw error;
    }
    throw new Error("Unknown error occurred");
  }
}

/**
 * Dashboard API functions.
 * Note: There's no consolidated /api/dashboard endpoint in the backend.
 * We'll need to fetch data from multiple endpoints and combine them.
 */
export const dashboardApi = {
  /**
   * Fetch dashboard data by combining multiple endpoints.
   * This is a composite function that fetches from alerts, fields, and recommendations.
   *
   * @returns Combined dashboard data
   */
  getDashboard: async () => {
    // Fetch critical alerts, recent recommendations, and fields in parallel
    const [criticalAlerts, recommendations, fields] = await Promise.all([
      apiFetch<{ alerts: unknown[]; count: number }>(`${API_ENDPOINTS.ALERTS}/critical?limit=5`),
      apiFetch<{ recommendations: unknown[]; total: number }>(
        `${API_ENDPOINTS.IRRIGATION_RECOMMENDATIONS}?page=1&page_size=5`
      ),
      apiFetch<{ fields: unknown[]; total: number }>(
        `${API_ENDPOINTS.FIELDS}?page=1&page_size=10`
      ),
    ]);

    return {
      criticalAlerts: criticalAlerts.alerts,
      recentRecommendations: recommendations.recommendations,
      fields: fields.fields,
    };
  },
};

/**
 * Irrigation API functions.
 * Connected to Agent 1's `/api/agents/irrigation/recommendations` endpoint.
 */
export const irrigationApi = {
  /**
   * Fetch irrigation recommendations for a field.
   *
   * @param params - Query parameters
   * @returns Paginated list of irrigation recommendations
   */
  getRecommendations: (params?: {
    field_id?: string;
    accepted?: boolean;
    page?: number;
    page_size?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.field_id) searchParams.set("field_id", params.field_id);
    if (params?.accepted !== undefined) searchParams.set("accepted", params.accepted.toString());
    if (params?.page) searchParams.set("page", params.page.toString());
    if (params?.page_size) searchParams.set("page_size", params.page_size.toString());

    const url = searchParams.toString()
      ? `${API_ENDPOINTS.IRRIGATION_RECOMMENDATIONS}?${searchParams.toString()}`
      : API_ENDPOINTS.IRRIGATION_RECOMMENDATIONS;
    return apiFetch<{ recommendations: unknown[]; total: number; page: number; page_size: number }>(url);
  },
  /**
   * Accept a recommendation.
   *
   * @param recommendationId - Recommendation UUID
   * @returns Updated recommendation
   */
  acceptRecommendation: (recommendationId: string) =>
    apiFetch(`/api/recommendations/${recommendationId}/accept`, {
      method: "POST",
    }),
};

/**
 * Fields API functions.
 * Connected to Agent 1's `/api/fields` endpoints.
 */
export const fieldsApi = {
  /**
   * Fetch all fields with optional filters.
   *
   * @param params - Query parameters
   * @returns Paginated list of fields
   */
  getFields: (params?: {
    farm_id?: string;
    crop_type?: string;
    page?: number;
    page_size?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.farm_id) searchParams.set("farm_id", params.farm_id);
    if (params?.crop_type) searchParams.set("crop_type", params.crop_type);
    if (params?.page) searchParams.set("page", params.page.toString());
    if (params?.page_size) searchParams.set("page_size", params.page_size.toString());

    const url = searchParams.toString()
      ? `${API_ENDPOINTS.FIELDS}?${searchParams.toString()}`
      : API_ENDPOINTS.FIELDS;
    return apiFetch<{ fields: unknown[]; total: number; page: number; page_size: number }>(url);
  },
  /**
   * Fetch a single field by ID with detailed information.
   *
   * @param fieldId - Field UUID
   * @returns Field details with sensor readings and fire risk data
   */
  getField: (fieldId: string) =>
    apiFetch<{ field: unknown; latest_sensor_reading: unknown | null; fire_risk_data: unknown | null }>(
      `${API_ENDPOINTS.FIELDS}/${fieldId}`
    ),
};

/**
 * Fire Risk API functions.
 * Note: Fire risk data is included in field details endpoint.
 * This is a placeholder for future dedicated fire risk endpoints.
 */
export const fireRiskApi = {
  /**
   * Fetch fire risk data.
   * Currently returns null as there's no dedicated endpoint.
   * Fire risk data is included in field details.
   *
   * @returns Fire risk zones and forecasts (null for now)
   */
  getFireRisk: async () => {
    // Fire risk data is fetched via fieldsApi.getField()
    return null;
  },
};

/**
 * Alerts API functions.
 * Connected to Agent 2's `/api/alerts` endpoints.
 */
export const alertsApi = {
  /**
   * Fetch alerts with optional filters.
   *
   * @param params - Query parameters for filtering and sorting
   * @returns Paginated list of alerts
   */
  getAlerts: (params?: {
    field_id?: string;
    severity?: "critical" | "warning" | "info";
    alert_type?: string;
    agent_type?: string;
    acknowledged?: boolean;
    page?: number;
    page_size?: number;
  }) => {
    const searchParams = new URLSearchParams();
    if (params?.field_id) searchParams.set("field_id", params.field_id);
    if (params?.severity) searchParams.set("severity", params.severity);
    if (params?.alert_type) searchParams.set("alert_type", params.alert_type);
    if (params?.agent_type) searchParams.set("agent_type", params.agent_type);
    if (params?.acknowledged !== undefined)
      searchParams.set("acknowledged", params.acknowledged.toString());
    if (params?.page) searchParams.set("page", params.page.toString());
    if (params?.page_size) searchParams.set("page_size", params.page_size.toString());

    const url = searchParams.toString()
      ? `${API_ENDPOINTS.ALERTS}?${searchParams.toString()}`
      : API_ENDPOINTS.ALERTS;
    return apiFetch<{ alerts: unknown[]; total: number; page: number; page_size: number }>(url);
  },
  /**
   * Get critical alerts for dashboard.
   *
   * @param params - Optional parameters
   * @returns List of critical alerts
   */
  getCriticalAlerts: (params?: { field_id?: string; limit?: number }) => {
    const searchParams = new URLSearchParams();
    if (params?.field_id) searchParams.set("field_id", params.field_id);
    if (params?.limit) searchParams.set("limit", params.limit.toString());

    const url = searchParams.toString()
      ? `${API_ENDPOINTS.ALERTS}/critical?${searchParams.toString()}`
      : `${API_ENDPOINTS.ALERTS}/critical`;
    return apiFetch<{ alerts: unknown[]; count: number }>(url);
  },
  /**
   * Acknowledge an alert.
   *
   * @param alertId - Alert UUID
   * @returns Updated alert
   */
  acknowledgeAlert: (alertId: string) =>
    apiFetch(`${API_ENDPOINTS.ALERTS}/${alertId}/acknowledge`, {
      method: "POST",
    }),
};

/**
 * Metrics API functions.
 * Connected to Agent 2's `/api/metrics` endpoints.
 */
export const metricsApi = {
  /**
   * Fetch water usage metrics for a field.
   *
   * @param fieldId - Field UUID
   * @param period - Time period ("season", "month", "week", or "all")
   * @returns Water metrics data
   */
  getWaterMetrics: (fieldId: string, period = "season") =>
    apiFetch<unknown>(`${API_ENDPOINTS.METRICS_WATER}?field_id=${fieldId}&period=${period}`),
  /**
   * Fetch farm-wide water summary.
   *
   * @param farmId - Farm ID
   * @returns Farm-wide water metrics summary
   */
  getWaterSummary: (farmId: string) =>
    apiFetch<unknown>(`${API_ENDPOINTS.METRICS_WATER}/summary?farm_id=${farmId}`),
  /**
   * Fetch fire risk metrics for a field.
   *
   * @param fieldId - Field UUID
   * @returns Fire risk reduction data and trends
   */
  getFireRiskMetrics: (fieldId: string) =>
    apiFetch<unknown>(`${API_ENDPOINTS.METRICS_FIRE_RISK}?field_id=${fieldId}`),
};

/**
 * Chat API functions.
 * Connected to Agent 1's `/api/agents/chat` endpoint.
 */
export const chatApi = {
  /**
   * Send a chat message to the agent.
   *
   * @param message - User message content
   * @param options - Optional chat options
   * @returns Agent response with message and conversation ID
   */
  sendMessage: async (
    message: string,
    options?: {
      conversation_id?: string;
      field_id?: string;
      include_context?: boolean;
    }
  ) => {
    const body: {
      message: string;
      conversation_id?: string;
      field_id?: string;
      include_context?: boolean;
    } = { message };

    if (options?.conversation_id) body.conversation_id = options.conversation_id;
    if (options?.field_id) body.field_id = options.field_id;
    if (options?.include_context !== undefined)
      body.include_context = options.include_context;

    return apiFetch<{
      message: string;
      conversation_id: string;
      sources?: string[];
      suggested_actions?: Array<{
        label: string;
        action: string;
        field_id?: string;
      }>;
    }>(API_ENDPOINTS.CHAT, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },
};

