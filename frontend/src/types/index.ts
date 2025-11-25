/**
 * TypeScript type definitions matching backend models.
 */

export interface User {
  id: string
  username: string
  email: string | null
  avatar_url: string | null
  github_id: number
  created_at: string
}

export interface Repository {
  id: string
  user_id: string
  github_id: number
  name: string
  full_name: string
  owner: string
  description: string | null
  private: boolean
  webhook_configured: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PullRequest {
  id: string
  repository_id: string
  pr_number: number
  title: string
  description: string | null
  author: string
  state: string
  base_branch: string
  head_branch: string
  files_changed: number
  additions: number
  deletions: number
  github_url: string
  created_at: string
  updated_at: string
}

export interface Review {
  id: string
  pull_request_id: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  critical_count: number
  warning_count: number
  info_count: number
  overall_score: number | null
  summary: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface Finding {
  id: string
  review_id: string
  category: string
  severity: 'critical' | 'warning' | 'info'
  title: string
  description: string
  file_path: string | null
  line_number: number | null
  code_snippet: string | null
  suggestion: string | null
  tool_source: string | null
  created_at: string
}

export interface ReviewStats {
  total_reviews: number
  pending_reviews: number
  in_progress_reviews: number
  completed_reviews: number
  failed_reviews: number
  avg_score: number | null
  total_critical_findings: number
  total_warning_findings: number
  total_info_findings: number
}

// API response types
export interface PaginatedResponse<T> {
  total: number
  items: T[]
}

export interface RepositoryListResponse {
  total: number
  repositories: Repository[]
}

export interface PullRequestListResponse {
  total: number
  pull_requests: PullRequest[]
}

export interface ReviewListResponse {
  total: number
  reviews: Review[]
}

export interface FindingListResponse {
  total: number
  findings: Finding[]
  critical_count: number
  warning_count: number
  info_count: number
}

// Request types
export interface CreateRepositoryRequest {
  github_id: number
  name: string
  full_name: string
  owner: string
  description?: string
  private: boolean
  configure_webhook?: boolean
}

export interface UpdateRepositoryRequest {
  name?: string
  description?: string
  is_active?: boolean
}

export interface CreateReviewRequest {
  pull_request_id: string
}

// Auth types
export interface LoginRequest {
  code: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}
