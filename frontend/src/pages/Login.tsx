/**
 * Login page with GitHub OAuth.
 */

import { Github, Code2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../components/ui/card'
import { redirectToGitHubOAuth } from '../lib/auth'

export function Login() {
  const handleGitHubLogin = () => {
    redirectToGitHubOAuth()
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 px-4">
      <div className="w-full max-w-md">
        {/* Logo and branding */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center space-x-2 mb-4">
            <Code2 className="h-12 w-12 text-primary" />
            <h1 className="text-3xl font-bold">AI Code Review</h1>
          </div>
          <p className="text-muted-foreground text-center">
            Automated code review powered by AI and static analysis
          </p>
        </div>

        {/* Login card */}
        <Card>
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Welcome back</CardTitle>
            <CardDescription className="text-center">
              Sign in with your GitHub account to continue
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button
              className="w-full"
              size="lg"
              onClick={handleGitHubLogin}
            >
              <Github className="mr-2 h-5 w-5" />
              Continue with GitHub
            </Button>

            <div className="text-xs text-center text-muted-foreground">
              By signing in, you agree to our Terms of Service and Privacy Policy
            </div>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="mt-8 space-y-3">
          <p className="text-sm font-medium text-center text-muted-foreground">
            What you'll get:
          </p>
          <div className="space-y-2">
            {[
              'AI-powered code analysis with Claude',
              'Security vulnerability detection',
              'Code quality and complexity metrics',
              'Automated PR review comments',
            ].map((feature, index) => (
              <div
                key={index}
                className="flex items-center space-x-2 text-sm text-muted-foreground"
              >
                <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                <span>{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
