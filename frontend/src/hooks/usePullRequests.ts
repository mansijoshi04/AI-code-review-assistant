/**
 * React Query hooks for pull request operations.
 */

import { useQuery } from '@tanstack/react-query'
import api from '../lib/api'
import type { PullRequest, PullRequestListResponse } from '../types'

/**
 * Fetch all pull requests for a repository.
 */
export function usePullRequests(
  repositoryId: string,
  params?: {
    state?: string
    skip?: number
    limit?: number
  }
) {
  return useQuery({
    queryKey: ['pull-requests', repositoryId, params],
    queryFn: async () => {
      const response = await api.get<PullRequestListResponse>(
        `/api/repositories/${repositoryId}/pulls`,
        { params }
      )
      return response.data
    },
    enabled: !!repositoryId,
  })
}

/**
 * Fetch a single pull request by ID.
 */
export function usePullRequest(id: string) {
  return useQuery({
    queryKey: ['pull-request', id],
    queryFn: async () => {
      const response = await api.get<PullRequest>(`/api/pulls/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}
