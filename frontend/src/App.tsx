/**
 * Main App component with React Router configuration.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from './components/ui/sonner'
import { ErrorBoundary } from './components/ErrorBoundary'
import { Layout } from './components/layout/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Login } from './pages/Login'
import { GitHubCallback } from './pages/GitHubCallback'
import { Dashboard } from './pages/Dashboard'
import { Repositories } from './pages/Repositories'
import { PullRequests } from './pages/PullRequests'
import { Reviews } from './pages/Reviews'
import { ReviewDetail } from './pages/ReviewDetail'

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/auth/github/callback" element={<GitHubCallback />} />

            {/* Protected routes with layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/repositories"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Repositories />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/repositories/:repositoryId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <PullRequests />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/reviews"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Reviews />
                  </Layout>
                </ProtectedRoute>
              }
            />

            <Route
              path="/reviews/:reviewId"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ReviewDetail />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Redirect root to dashboard if authenticated, otherwise to login */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />

            {/* 404 - redirect to dashboard */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
          <Toaster />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  )
}

export default App
