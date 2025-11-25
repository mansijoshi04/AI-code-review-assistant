/**
 * Zustand store for authentication state management.
 */

import { create } from 'zustand'
import { User } from '../types'
import {
  getToken,
  getUser,
  setToken as saveToken,
  setUser as saveUser,
  clearAuth,
} from '../lib/auth'

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
  updateUser: (user: User) => void
}

/**
 * Auth store with persistence to localStorage.
 */
export const useAuthStore = create<AuthState>((set) => ({
  // Initialize from localStorage
  token: getToken(),
  user: getUser(),
  isAuthenticated: !!getToken(),

  /**
   * Login: Save token and user, mark as authenticated.
   */
  login: (token: string, user: User) => {
    saveToken(token)
    saveUser(user)
    set({
      token,
      user,
      isAuthenticated: true,
    })
  },

  /**
   * Logout: Clear token and user, mark as not authenticated.
   */
  logout: () => {
    clearAuth()
    set({
      token: null,
      user: null,
      isAuthenticated: false,
    })
  },

  /**
   * Update user data (e.g., after profile update).
   */
  updateUser: (user: User) => {
    saveUser(user)
    set({ user })
  },
}))
