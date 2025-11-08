/**
 * React Query hook for fetching irrigation recommendations.
 *
 * Connected to Agent 1's `/api/agents/irrigation/recommendations` endpoint.
 *
 * @module hooks/useRecommendations
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { irrigationApi } from "../api";
import type { Recommendation, RecommendationListResponse } from "../types";
import { toast } from "sonner";

/**
 * Query key factory for recommendations.
 */
export const recommendationsQueryKey = (params?: {
  field_id?: string;
  accepted?: boolean;
  page?: number;
}) => ["recommendations", params] as const;

/**
 * Hook to fetch irrigation recommendations.
 *
 * @param params - Query parameters for filtering recommendations
 * @returns React Query query object with recommendations data
 */
export function useRecommendations(params?: {
  field_id?: string;
  accepted?: boolean;
  page?: number;
  page_size?: number;
}) {
  return useQuery<RecommendationListResponse>({
    queryKey: recommendationsQueryKey(params),
    queryFn: () =>
      irrigationApi.getRecommendations(params) as Promise<RecommendationListResponse>,
    staleTime: 2 * 60 * 1000, // 2 minutes
    retry: false, // Don't retry on connection errors
    refetchOnWindowFocus: false, // Don't refetch on window focus if backend is down
  });
}

/**
 * Hook to accept a recommendation.
 *
 * @returns Mutation function to accept a recommendation
 */
export function useAcceptRecommendation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (recommendationId: string) =>
      irrigationApi.acceptRecommendation(recommendationId),
    onSuccess: () => {
      // Invalidate recommendations queries to refetch updated data
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      toast.success("Recommendation accepted successfully");
    },
    onError: (error: Error) => {
      toast.error(`Failed to accept recommendation: ${error.message}`);
    },
  });
}

