/**
 * GitHub OAuth callback handler page.
 */

import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api, { getErrorMessage } from '../lib/api'
import { TokenResponse } from '../types'
import { Loader2, AlertCircle } from 'lucide-react'
import { Card, CardContent } from '../components/ui/card'

export function GitHubCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const handleCallback = async () => {
      // Get authorization code from URL
      const code = searchParams.get('code')
      const error = searchParams.get('error')

      if (error) {
        setError(`GitHub authorization failed: ${error}`)
        setTimeout(() => navigate('/login'), 3000)
        return
      }

      if (!code) {
        setError('No authorization code received from GitHub')
        setTimeout(() => navigate('/login'), 3000)
        return
      }

      try {
        // Exchange code for token
        const response = await api.post<TokenResponse>('/api/auth/github', {
          code,
        })

        const { access_token, user } = response.data

        // Save to store and localStorage
        login(access_token, user)

        // Redirect to dashboard
        navigate('/dashboard')
      } catch (err) {
        const errorMsg = getErrorMessage(err)
        setError(`Authentication failed: ${errorMsg}`)
        setTimeout(() => navigate('/login'), 3000)
      }
    }

    handleCallback()
  }, [searchParams, login, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 px-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6">
          {error ? (
            <div className="flex flex-col items-center space-y-4 text-center">
              <AlertCircle className="h-12 w-12 text-destructive" />
              <div>
                <h2 className="text-xl font-semibold mb-2">
                  Authentication Error
                </h2>
                <p className="text-sm text-muted-foreground">{error}</p>
                <p className="text-xs text-muted-foreground mt-2">
                  Redirecting to login...
                </p>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-4 text-center">
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
              <div>
                <h2 className="text-xl font-semibold mb-2">
                  Completing sign in...
                </h2>
                <p className="text-sm text-muted-foreground">
                  Please wait while we authenticate your account
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
