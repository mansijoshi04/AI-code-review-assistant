/**
 * Repositories page for managing GitHub repositories.
 */

import { Link } from 'react-router-dom'
import { useRepositories } from '../hooks/useRepositories'
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
import { GitBranch, RefreshCw, ExternalLink, Loader2 } from 'lucide-react'
import { formatDate } from '../lib/utils'

export function Repositories() {
  const { data, isLoading, error } = useRepositories()

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
            Error loading repositories. Please try again.
          </div>
        </CardContent>
      </Card>
    )
  }

  const repositories = data?.repositories || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Repositories</h1>
          <p className="text-muted-foreground mt-2">
            Manage your GitHub repositories and configure code reviews
          </p>
        </div>
        <Button>
          <GitBranch className="mr-2 h-4 w-4" />
          Add Repository
        </Button>
      </div>

      {/* Repositories table */}
      <Card>
        <CardHeader>
          <CardTitle>Your Repositories</CardTitle>
          <CardDescription>
            {repositories.length} repositories configured for code review
          </CardDescription>
        </CardHeader>
        <CardContent>
          {repositories.length === 0 ? (
            <div className="text-center py-12">
              <GitBranch className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No repositories yet</h3>
              <p className="text-muted-foreground mb-4">
                Add your first repository to start reviewing code
              </p>
              <Button>Add Repository</Button>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Owner</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Webhook</TableHead>
                  <TableHead>Updated</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {repositories.map((repo) => (
                  <TableRow key={repo.id}>
                    <TableCell>
                      <Link
                        to={`/repositories/${repo.id}`}
                        className="font-medium hover:underline"
                      >
                        {repo.name}
                      </Link>
                      {repo.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {repo.description}
                        </p>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {repo.owner}
                    </TableCell>
                    <TableCell>
                      <Badge variant={repo.is_active ? 'default' : 'secondary'}>
                        {repo.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          repo.webhook_configured ? 'default' : 'outline'
                        }
                      >
                        {repo.webhook_configured ? 'Configured' : 'Not set'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm">
                      {formatDate(repo.updated_at)}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <Button variant="ghost" size="sm" asChild>
                          <a
                            href={`https://github.com/${repo.full_name}`}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        </Button>
                        <Button variant="ghost" size="sm">
                          <RefreshCw className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
