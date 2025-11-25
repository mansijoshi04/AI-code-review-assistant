/**
 * Pull requests page showing PRs for a repository.
 */

import { Link, useParams } from 'react-router-dom'
import { usePullRequests } from '../hooks/usePullRequests'
import { useRepository } from '../hooks/useRepositories'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../components/ui/table'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { GitPullRequest, Loader2, ArrowLeft, ExternalLink } from 'lucide-react'
import { formatDate } from '../lib/utils'
import { useState } from 'react'

export function PullRequests() {
  const { repositoryId } = useParams<{ repositoryId: string }>()
  const [stateFilter, setStateFilter] = useState<string>('all')

  const { data: repo } = useRepository(repositoryId!)
  const { data, isLoading, error } = usePullRequests(repositoryId!, {
    state: stateFilter === 'all' ? undefined : stateFilter,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-destructive">
            Error loading pull requests. Please try again.
          </div>
        </CardContent>
      </Card>
    )
  }

  const pullRequests = data?.pull_requests || []

  return (
    <div className="space-y-6">
      {/* Header with back button */}
      <div>
        <Button variant="ghost" asChild className="mb-4">
          <Link to="/repositories">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Repositories
          </Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{repo?.name || 'Repository'}</h1>
            <p className="text-muted-foreground mt-2">
              Pull requests for {repo?.full_name}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs for filtering */}
      <Tabs value={stateFilter} onValueChange={setStateFilter}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="open">Open</TabsTrigger>
          <TabsTrigger value="closed">Closed</TabsTrigger>
          <TabsTrigger value="merged">Merged</TabsTrigger>
        </TabsList>

        <TabsContent value={stateFilter} className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Pull Requests</CardTitle>
              <CardDescription>
                {pullRequests.length} pull requests found
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pullRequests.length === 0 ? (
                <div className="text-center py-12">
                  <GitPullRequest className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">
                    No pull requests found
                  </h3>
                  <p className="text-muted-foreground">
                    {stateFilter === 'all'
                      ? 'This repository has no pull requests yet'
                      : `No ${stateFilter} pull requests`}
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Title</TableHead>
                      <TableHead>Author</TableHead>
                      <TableHead>State</TableHead>
                      <TableHead>Changes</TableHead>
                      <TableHead>Created</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pullRequests.map((pr) => (
                      <TableRow key={pr.id}>
                        <TableCell>
                          <Link
                            to={`/pull-requests/${pr.id}`}
                            className="font-medium hover:underline"
                          >
                            #{pr.pr_number} {pr.title}
                          </Link>
                          {pr.description && (
                            <p className="text-sm text-muted-foreground mt-1 line-clamp-1">
                              {pr.description}
                            </p>
                          )}
                          <div className="flex items-center space-x-2 mt-1 text-xs text-muted-foreground">
                            <span>{pr.base_branch}</span>
                            <span>←</span>
                            <span>{pr.head_branch}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground">
                          {pr.author}
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              pr.state === 'open'
                                ? 'default'
                                : pr.state === 'merged'
                                ? 'secondary'
                                : 'outline'
                            }
                          >
                            {pr.state}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-sm">
                          <div className="flex flex-col space-y-1">
                            <span className="text-green-600">
                              +{pr.additions}
                            </span>
                            <span className="text-red-600">
                              -{pr.deletions}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell className="text-muted-foreground text-sm">
                          {formatDate(pr.created_at)}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm" asChild>
                            <a
                              href={pr.github_url}
                              target="_blank"
                              rel="noopener noreferrer"
                            >
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
