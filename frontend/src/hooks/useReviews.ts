/**
 * React Query hooks for review operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import type {
  Review,
  ReviewListResponse,
  FindingListResponse,
  ReviewStats,
} from '../types'

/**
 * Fetch all reviews.
 */
export function useReviews(params?: {
  status_filter?: string
  skip?: number
  limit?: number
}) {
  return useQuery({
    queryKey: ['reviews', params],
    queryFn: async () => {
      const response = await api.get<ReviewListResponse>('/api/reviews', {
        params,
      })
      return response.data
    },
  })
}

/**
 * Fetch a single review by ID.
 */
export function useReview(id: string) {
  return useQuery({
    queryKey: ['review', id],
    queryFn: async () => {
      const response = await api.get<Review>(`/api/reviews/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

/**
 * Fetch findings for a review.
 */
export function useReviewFindings(
  reviewId: string,
  params?: {
    severity?: string
    category?: string
    skip?: number
    limit?: number
  }
) {
  return useQuery({
    queryKey: ['review-findings', reviewId, params],
    queryFn: async () => {
      const response = await api.get<FindingListResponse>(
        `/api/reviews/${reviewId}/findings`,
        { params }
      )
      return response.data
    },
    enabled: !!reviewId,
  })
}

/**
 * Create a new review for a pull request.
 */
export function useCreateReview() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (pullRequestId: string) => {
      const response = await api.post<Review>(
        `/api/pulls/${pullRequestId}/reviews`
      )
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] })
    },
  })
}

/**
 * Fetch review statistics.
 */
export function useReviewStats() {
  return useQuery({
    queryKey: ['review-stats'],
    queryFn: async () => {
      const response = await api.get<ReviewStats>('/api/stats')
      return response.data
    },
  })
}
