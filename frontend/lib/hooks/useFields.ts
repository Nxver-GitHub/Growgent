/**
 * React Query hook for fetching fields data.
 *
 * Connected to Agent 1's `/api/fields` endpoints.
 *
 * @module hooks/useFields
 */

import { useQuery } from "@tanstack/react-query";
import { fieldsApi } from "../api";
import type { Field, FieldListResponse, FieldDetailResponse } from "../types";

/**
 * Query key factory for fields list.
 */
export const fieldsQueryKey = (params?: {
  farm_id?: string;
  crop_type?: string;
  page?: number;
  page_size?: number;
}) => ["fields", params] as const;

/**
 * Query key factory for single field.
 */
export const fieldQueryKey = (fieldId: string) => ["field", fieldId] as const;

/**
 * Hook to fetch fields with optional filters.
 *
 * @param params - Query parameters for filtering fields
 * @returns React Query query object with fields data
 */
export function useFields(params?: {
  farm_id?: string;
  crop_type?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery<FieldListResponse>({
    queryKey: fieldsQueryKey(params),
    queryFn: () => fieldsApi.getFields(params) as Promise<FieldListResponse>,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to fetch a single field by ID with detailed information.
 *
 * @param fieldId - Field UUID
 * @returns React Query query object with field details
 */
export function useField(fieldId: string | null) {
  return useQuery<FieldDetailResponse>({
    queryKey: fieldQueryKey(fieldId || ""),
    queryFn: () => fieldsApi.getField(fieldId!) as Promise<FieldDetailResponse>,
    enabled: !!fieldId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

