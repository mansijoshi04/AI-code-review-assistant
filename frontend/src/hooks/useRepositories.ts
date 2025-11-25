/**
 * React Query hooks for repository operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../lib/api'
import type {
  RepositoryListResponse,
  Repository,
  CreateRepositoryRequest,
  UpdateRepositoryRequest,
} from '../types'

/**
 * Fetch all repositories for the authenticated user.
 */
export function useRepositories(isActive?: boolean) {
  return useQuery({
    queryKey: ['repositories', isActive],
    queryFn: async () => {
      const params = isActive !== undefined ? { is_active: isActive } : {}
      const response = await api.get<RepositoryListResponse>('/api/repositories', {
        params,
      })
      return response.data
    },
  })
}

/**
 * Fetch a single repository by ID.
 */
export function useRepository(id: string) {
  return useQuery({
    queryKey: ['repository', id],
    queryFn: async () => {
      const response = await api.get<Repository>(`/api/repositories/${id}`)
      return response.data
    },
    enabled: !!id,
  })
}

/**
 * Create a new repository.
 */
export function useCreateRepository() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateRepositoryRequest) => {
      const response = await api.post<Repository>('/api/repositories', data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
    },
  })
}

/**
 * Update a repository.
 */
export function useUpdateRepository(id: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: UpdateRepositoryRequest) => {
      const response = await api.put<Repository>(`/api/repositories/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
      queryClient.invalidateQueries({ queryKey: ['repository', id] })
    },
  })
}

/**
 * Delete a repository.
 */
export function useDeleteRepository() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/api/repositories/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
    },
  })
}

/**
 * Sync repositories from GitHub.
 */
export function useSyncRepository(id: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async () => {
      const response = await api.post(`/api/repositories/${id}/sync`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories'] })
      queryClient.invalidateQueries({ queryKey: ['repository', id] })
    },
  })
}
