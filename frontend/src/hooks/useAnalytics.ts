/**
 * React Query hooks for analytics and dashboard data.
 */

import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import type {
  ReviewTrendsResponse,
  FindingsDistributionResponse,
  RepositoryActivityResponse,
} from '../types'

/**
 * Fetch review trends over time.
 */
export function useReviewTrends(period: '7d' | '30d' | '90d' = '30d') {
  return useQuery({
    queryKey: ['analytics', 'trends', period],
    queryFn: async () => {
      const response = await api.get<ReviewTrendsResponse>(
        '/api/analytics/trends',
        {
          params: { period },
        }
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Fetch findings distribution by category.
 */
export function useFindingsDistribution() {
  return useQuery({
    queryKey: ['analytics', 'findings-distribution'],
    queryFn: async () => {
      const response = await api.get<FindingsDistributionResponse>(
        '/api/analytics/findings-distribution'
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Fetch repository activity statistics.
 */
export function useRepositoryActivity(limit: number = 10) {
  return useQuery({
    queryKey: ['analytics', 'repository-activity', limit],
    queryFn: async () => {
      const response = await api.get<RepositoryActivityResponse>(
        '/api/analytics/repository-activity',
        {
          params: { limit },
        }
      )
      return response.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}
