/**
 * React Query hook for fetching alerts.
 *
 * Connected to Agent 2's `/api/alerts` endpoint.
 *
 * @module hooks/useAlerts
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "../api";
import { PAGINATION, POLLING_INTERVALS } from "../constants";
import type { Alert, AlertListResponse } from "../types";
import { toast } from "sonner";

/**
 * Query key factory for alerts.
 */
export const alertsQueryKey = (params?: {
  field_id?: string;
  severity?: "critical" | "warning" | "info";
  alert_type?: string;
  agent_type?: string;
  acknowledged?: boolean;
  page?: number;
}) => ["alerts", params] as const;

/**
 * Hook to fetch alerts with optional filters.
 *
 * @param params - Optional query parameters for filtering and sorting
 * @param options - Additional query options (e.g., polling interval)
 * @returns React Query query object with alerts data
 */
export function useAlerts(
  params?: {
    field_id?: string;
    severity?: "critical" | "warning" | "info";
    alert_type?: string;
    agent_type?: string;
    acknowledged?: boolean;
    page?: number;
    page_size?: number;
  },
  options?: {
    enablePolling?: boolean;
  }
) {
  return useQuery<AlertListResponse>({
    queryKey: alertsQueryKey(params),
    queryFn: () =>
      alertsApi.getAlerts({
        ...params,
        page_size: params?.page_size || PAGINATION.ALERTS_PAGE_SIZE,
      }) as Promise<AlertListResponse>,
    // Poll every 30 seconds if enabled
    refetchInterval: options?.enablePolling ? POLLING_INTERVALS.ALERTS : false,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
}

/**
 * Hook to fetch critical alerts for dashboard.
 *
 * @param params - Optional parameters
 * @returns React Query query object with critical alerts
 */
export function useCriticalAlerts(params?: { field_id?: string; limit?: number }) {
  return useQuery<{ alerts: Alert[]; count: number }>({
    queryKey: ["alerts", "critical", params],
    queryFn: () => alertsApi.getCriticalAlerts(params) as Promise<{ alerts: Alert[]; count: number }>,
    staleTime: 1 * 60 * 1000, // 1 minute
    refetchInterval: POLLING_INTERVALS.ALERTS, // Poll every 30 seconds
    retry: false, // Don't retry on connection errors
    refetchOnWindowFocus: false, // Don't refetch on window focus if backend is down
  });
}

/**
 * Hook to acknowledge an alert.
 *
 * @returns Mutation function to acknowledge an alert
 */
export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => alertsApi.acknowledgeAlert(alertId),
    onSuccess: () => {
      // Invalidate alerts queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      toast.success("Alert acknowledged");
    },
    onError: (error: Error) => {
      toast.error(`Failed to acknowledge alert: ${error.message}`);
    },
  });
}

