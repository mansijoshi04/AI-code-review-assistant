/**
 * Authentication utility functions.
 */

import { User } from '../types'

const TOKEN_KEY = 'auth_token'
const USER_KEY = 'auth_user'

/**
 * Store authentication token in localStorage.
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * Get authentication token from localStorage.
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Remove authentication token from localStorage.
 */
export function removeToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * Store user data in localStorage.
 */
export function setUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/**
 * Get user data from localStorage.
 */
export function getUser(): User | null {
  const userStr = localStorage.getItem(USER_KEY)
  if (!userStr) return null
  try {
    return JSON.parse(userStr)
  } catch {
    return null
  }
}

/**
 * Remove user data from localStorage.
 */
export function removeUser(): void {
  localStorage.removeItem(USER_KEY)
}

/**
 * Clear all authentication data.
 */
export function clearAuth(): void {
  removeToken()
  removeUser()
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return !!getToken()
}

/**
 * Redirect to GitHub OAuth authorization.
 */
export function redirectToGitHubOAuth(): void {
  const clientId = import.meta.env.VITE_GITHUB_CLIENT_ID
  const redirectUri = window.location.origin + '/auth/github/callback'
  const scope = 'read:user user:email repo'

  const authUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`
  window.location.href = authUrl
}
