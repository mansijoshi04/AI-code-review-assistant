/**
 * Reviews list page showing all code reviews.
 */

import { Link } from 'react-router-dom'
import { useReviews } from '../hooks/useReviews'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { FileSearch, Loader2 } from 'lucide-react'
import { formatDateTime, getScoreColor } from '../lib/utils'
import { useState } from 'react'

export function Reviews() {
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const { data, isLoading, error } = useReviews({
    status_filter: statusFilter === 'all' ? undefined : statusFilter,
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
            Error loading reviews. Please try again.
          </div>
        </CardContent>
      </Card>
    )
  }

  const reviews = data?.reviews || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Code Reviews</h1>
        <p className="text-muted-foreground mt-2">
          View all code reviews and their findings
        </p>
      </div>

      {/* Tabs for filtering */}
      <Tabs value={statusFilter} onValueChange={setStatusFilter}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="in_progress">In Progress</TabsTrigger>
          <TabsTrigger value="failed">Failed</TabsTrigger>
        </TabsList>

        <TabsContent value={statusFilter} className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Reviews</CardTitle>
              <CardDescription>
                {reviews.length} reviews found
              </CardDescription>
            </CardHeader>
            <CardContent>
              {reviews.length === 0 ? (
                <div className="text-center py-12">
                  <FileSearch className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">
                    No reviews found
                  </h3>
                  <p className="text-muted-foreground">
                    {statusFilter === 'all'
                      ? 'No code reviews have been created yet'
                      : `No ${statusFilter} reviews`}
                  </p>
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Created</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Score</TableHead>
                      <TableHead>Critical</TableHead>
                      <TableHead>Warning</TableHead>
                      <TableHead>Info</TableHead>
                      <TableHead>Summary</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {reviews.map((review) => (
                      <TableRow key={review.id}>
                        <TableCell>
                          <Link
                            to={`/reviews/${review.id}`}
                            className="text-sm hover:underline"
                          >
                            {formatDateTime(review.created_at)}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              review.status === 'completed'
                                ? 'default'
                                : review.status === 'failed'
                                ? 'destructive'
                                : 'secondary'
                            }
                          >
                            {review.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {review.overall_score !== null ? (
                            <span
                              className={`font-semibold ${getScoreColor(review.overall_score)}`}
                            >
                              {review.overall_score}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-red-100 text-red-800 border-red-200">
                            {review.critical_count}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200">
                            {review.warning_count}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                            {review.info_count}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-md">
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {review.summary || 'No summary available'}
                          </p>
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
