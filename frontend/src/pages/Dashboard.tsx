/**
 * Dashboard page showing overview statistics.
 */

import { useAuthStore } from '../store/authStore'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Code2, GitPullRequest, AlertTriangle, CheckCircle2 } from 'lucide-react'

export function Dashboard() {
  const { user } = useAuthStore()

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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Total Reviews
            </CardTitle>
            <Code2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              No reviews yet
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Pull Requests
            </CardTitle>
            <GitPullRequest className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">
              Across all repositories
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
            <div className="text-2xl font-bold">0</div>
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
            <div className="text-2xl font-bold">-</div>
            <p className="text-xs text-muted-foreground">
              Quality metric
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Getting started card */}
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
                <div className="space-y-1">
                  <p className="font-medium leading-none">{item.title}</p>
                  <p className="text-sm text-muted-foreground">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
