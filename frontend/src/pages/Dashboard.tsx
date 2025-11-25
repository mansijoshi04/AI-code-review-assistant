/**
 * Dashboard page showing overview statistics.
 */

import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useReviewStats } from '../hooks/useReviews'
import { useRepositories } from '../hooks/useRepositories'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Code2, GitPullRequest, AlertTriangle, CheckCircle2, Loader2, TrendingUp } from 'lucide-react'
import { formatNumber, getScoreColor } from '../lib/utils'

export function Dashboard() {
  const { user } = useAuthStore()
  const { data: stats, isLoading: statsLoading } = useReviewStats()
  const { data: reposData, isLoading: reposLoading } = useRepositories()

  const isLoading = statsLoading || reposLoading
  const repositories = reposData?.repositories || []
  const activeRepos = repositories.filter((r) => r.is_active).length

  return (
    <div className="space-y-8">
      {/* Welcome header */}
      <div>
        <h1 className="text-3xl font-bold">Welcome back, {user?.username}!</h1>
        <p className="text-muted-foreground mt-2">
          Here's an overview of your code reviews
        </p>
      </div>

      {/* Stats cards */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Reviews
                </CardTitle>
                <Code2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(stats?.total_reviews || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats?.completed_reviews || 0} completed
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Repositories
                </CardTitle>
                <GitPullRequest className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(repositories.length)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {activeRepos} active
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Critical Issues
                </CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatNumber(stats?.total_critical_findings || 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  Need immediate attention
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  Average Score
                </CardTitle>
                <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div
                  className={`text-2xl font-bold ${getScoreColor(stats?.avg_score || 0)}`}
                >
                  {stats?.avg_score !== null && stats?.avg_score !== undefined
                    ? Math.round(stats.avg_score)
                    : '-'}
                </div>
                <p className="text-xs text-muted-foreground">
                  Quality metric
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Secondary stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Total Findings
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Critical</span>
                  <span className="font-semibold text-red-600">
                    {formatNumber(stats?.total_critical_findings || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Warning</span>
                  <span className="font-semibold text-yellow-600">
                    {formatNumber(stats?.total_warning_findings || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Info</span>
                  <span className="font-semibold text-blue-600">
                    {formatNumber(stats?.total_info_findings || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Review Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Completed</span>
                  <span className="font-semibold">
                    {formatNumber(stats?.completed_reviews || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">In Progress</span>
                  <span className="font-semibold">
                    {formatNumber(stats?.in_progress_reviews || 0)}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Pending</span>
                  <span className="font-semibold">
                    {formatNumber(stats?.pending_reviews || 0)}
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link to="/repositories">
                    <GitPullRequest className="mr-2 h-4 w-4" />
                    View Repositories
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-start" asChild>
                  <Link to="/reviews">
                    <TrendingUp className="mr-2 h-4 w-4" />
                    View All Reviews
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>
        </>
      )}

      {/* Getting started card */}
      {(stats?.total_reviews || 0) === 0 && !isLoading && (
        <Card>
          <CardHeader>
            <CardTitle>Getting Started</CardTitle>
            <CardDescription>
              Follow these steps to start reviewing your code
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              {[
                {
                  step: 1,
                  title: 'Connect a repository',
                  description: 'Add your GitHub repositories to enable automatic reviews',
                  action: (
                    <Button variant="link" className="p-0 h-auto" asChild>
                      <Link to="/repositories">Go to Repositories →</Link>
                    </Button>
                  ),
                },
                {
                  step: 2,
                  title: 'Configure webhooks',
                  description: 'Set up webhooks to automatically trigger reviews on new PRs',
                },
                {
                  step: 3,
                  title: 'Create a pull request',
                  description: 'Open a PR and watch the AI analyze your code automatically',
                },
              ].map((item) => (
                <div key={item.step} className="flex items-start space-x-4">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border bg-background text-sm font-medium">
                    {item.step}
                  </div>
                  <div className="space-y-1 flex-1">
                    <p className="font-medium leading-none">{item.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {item.description}
                    </p>
                    {item.action}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
