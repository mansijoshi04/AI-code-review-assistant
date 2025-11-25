/**
 * Main navigation bar component.
 */

import { Link } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Button } from '../ui/button'
import { Code2, LogOut, User } from 'lucide-react'

export function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo and brand */}
          <Link to="/" className="flex items-center space-x-2">
            <Code2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">AI Code Review</span>
          </Link>

          {/* Navigation links (when authenticated) */}
          {isAuthenticated && (
            <div className="hidden md:flex items-center space-x-6">
              <Link
                to="/dashboard"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Dashboard
              </Link>
              <Link
                to="/repositories"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Repositories
              </Link>
              <Link
                to="/reviews"
                className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
              >
                Reviews
              </Link>
            </div>
          )}

          {/* User menu */}
          <div className="flex items-center space-x-4">
            {isAuthenticated && user ? (
              <>
                <div className="hidden md:flex items-center space-x-2">
                  {user.avatar_url ? (
                    <img
                      src={user.avatar_url}
                      alt={user.username}
                      className="h-8 w-8 rounded-full border"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center border">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                  <span className="text-sm font-medium">{user.username}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="flex items-center space-x-2"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Logout</span>
                </Button>
              </>
            ) : (
              <Button asChild>
                <Link to="/login">Sign In</Link>
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
