/**
 * Review detail page showing findings and analysis.
 */

import { useParams, Link } from 'react-router-dom'
import { useReview, useReviewFindings } from '../hooks/useReviews'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { ArrowLeft, Loader2, AlertTriangle, AlertCircle, Info } from 'lucide-react'
import { formatDateTime, getSeverityColor, getCategoryColor, getScoreColor } from '../lib/utils'
import { useState } from 'react'

export function ReviewDetail() {
  const { reviewId } = useParams<{ reviewId: string }>()
  const [severityFilter, setSeverityFilter] = useState<string>('all')

  const { data: review, isLoading: reviewLoading } = useReview(reviewId!)
  const { data: findingsData, isLoading: findingsLoading } = useReviewFindings(
    reviewId!,
    {
      severity: severityFilter === 'all' ? undefined : severityFilter,
    }
  )

  if (reviewLoading || findingsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (!review) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-destructive">
            Review not found
          </div>
        </CardContent>
      </Card>
    )
  }

  const findings = findingsData?.findings || []

  return (
    <div className="space-y-6">
      {/* Header with back button */}
      <div>
        <Button variant="ghost" asChild className="mb-4">
          <Link to="/reviews">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Reviews
          </Link>
        </Button>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Code Review</h1>
            <p className="text-muted-foreground mt-2">
              Review from {formatDateTime(review.created_at)}
            </p>
          </div>
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
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${getScoreColor(review.overall_score || 0)}`}>
              {review.overall_score !== null ? review.overall_score : '-'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Out of 100
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{review.critical_count}</div>
            <p className="text-xs text-muted-foreground mt-1">
              High priority issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Warnings</CardTitle>
            <AlertCircle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{review.warning_count}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Should be addressed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3 flex flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm font-medium">Info</CardTitle>
            <Info className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{review.info_count}</div>
            <p className="text-xs text-muted-foreground mt-1">
              Informational findings
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Summary */}
      {review.summary && (
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {review.summary}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Findings tabs */}
      <Tabs value={severityFilter} onValueChange={setSeverityFilter}>
        <TabsList>
          <TabsTrigger value="all">
            All ({findingsData?.total || 0})
          </TabsTrigger>
          <TabsTrigger value="critical">
            Critical ({findingsData?.critical_count || 0})
          </TabsTrigger>
          <TabsTrigger value="warning">
            Warning ({findingsData?.warning_count || 0})
          </TabsTrigger>
          <TabsTrigger value="info">
            Info ({findingsData?.info_count || 0})
          </TabsTrigger>
        </TabsList>

        <TabsContent value={severityFilter} className="mt-6">
          <div className="space-y-4">
            {findings.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-8">
                    <h3 className="text-lg font-semibold mb-2">
                      No findings
                    </h3>
                    <p className="text-muted-foreground">
                      {severityFilter === 'all'
                        ? 'This review has no findings'
                        : `No ${severityFilter} findings`}
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              findings.map((finding) => (
                <Card key={finding.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <Badge className={getSeverityColor(finding.severity)}>
                            {finding.severity}
                          </Badge>
                          <Badge className={getCategoryColor(finding.category)}>
                            {finding.category}
                          </Badge>
                          {finding.tool_source && (
                            <span className="text-xs text-muted-foreground">
                              via {finding.tool_source}
                            </span>
                          )}
                        </div>
                        <CardTitle className="text-xl">{finding.title}</CardTitle>
                        {finding.file_path && (
                          <CardDescription>
                            {finding.file_path}
                            {finding.line_number && `:${finding.line_number}`}
                          </CardDescription>
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {finding.description && (
                      <div>
                        <h4 className="font-semibold mb-2">Description</h4>
                        <p className="text-sm text-muted-foreground">
                          {finding.description}
                        </p>
                      </div>
                    )}

                    {finding.code_snippet && (
                      <div>
                        <h4 className="font-semibold mb-2">Code</h4>
                        <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                          <code>{finding.code_snippet}</code>
                        </pre>
                      </div>
                    )}

                    {finding.suggestion && (
                      <div>
                        <h4 className="font-semibold mb-2">Suggestion</h4>
                        <p className="text-sm text-muted-foreground">
                          {finding.suggestion}
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
