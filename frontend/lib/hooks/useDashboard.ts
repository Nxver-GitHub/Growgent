/**
 * React Query hook for fetching dashboard data.
 *
 * Fetches data from multiple endpoints and combines them for the dashboard.
 *
 * @module hooks/useDashboard
 */

import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../api";
import type { Alert, Recommendation, Field } from "../types";

/**
 * Query key for dashboard data.
 */
export const dashboardQueryKey = ["dashboard"] as const;

/**
 * Dashboard data structure.
 */
export interface DashboardData {
  criticalAlerts: Alert[];
  recentRecommendations: Recommendation[];
  fields: Field[];
}

/**
 * Hook to fetch dashboard data.
 *
 * @returns React Query query object with dashboard data
 */
export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: dashboardQueryKey,
    queryFn: () => dashboardApi.getDashboard() as Promise<DashboardData>,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
    retry: false, // Don't retry on connection errors
    refetchOnWindowFocus: false, // Don't refetch on window focus if backend is down
  });
}

