/**
 * React Query hook for fetching metrics data.
 *
 * Connected to Agent 2's `/api/metrics` endpoints.
 *
 * @module hooks/useMetrics
 */

import { useQuery } from "@tanstack/react-query";
import { metricsApi } from "../api";
import type { WaterMetrics, FireRiskMetrics } from "../types";

/**
 * Query key factory for water metrics.
 */
export const waterMetricsQueryKey = (fieldId: string, period = "season") =>
  ["metrics", "water", fieldId, period] as const;

/**
 * Query key factory for fire risk metrics.
 */
export const fireRiskMetricsQueryKey = (fieldId: string) =>
  ["metrics", "fire-risk", fieldId] as const;

/**
 * Query key factory for water summary.
 */
export const waterSummaryQueryKey = (farmId: string) =>
  ["metrics", "water", "summary", farmId] as const;

/**
 * Hook to fetch water usage metrics for a field.
 *
 * @param fieldId - Field UUID
 * @param period - Time period ("season", "month", "week", or "all")
 * @returns React Query query object with water metrics data
 */
export function useWaterMetrics(fieldId: string, period = "season") {
  return useQuery<WaterMetrics>({
    queryKey: waterMetricsQueryKey(fieldId, period),
    queryFn: () => metricsApi.getWaterMetrics(fieldId, period) as Promise<WaterMetrics>,
    enabled: !!fieldId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch farm-wide water summary.
 *
 * @param farmId - Farm ID
 * @returns React Query query object with water summary data
 */
export function useWaterSummary(farmId: string) {
  return useQuery({
    queryKey: waterSummaryQueryKey(farmId),
    queryFn: () => metricsApi.getWaterSummary(farmId),
    enabled: !!farmId,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Hook to fetch fire risk metrics for a field.
 *
 * @param fieldId - Field UUID
 * @returns React Query query object with fire risk metrics data
 */
export function useFireRiskMetrics(fieldId: string) {
  return useQuery<FireRiskMetrics>({
    queryKey: fireRiskMetricsQueryKey(fieldId),
    queryFn: () => metricsApi.getFireRiskMetrics(fieldId) as Promise<FireRiskMetrics>,
    enabled: !!fieldId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

