/**
 * Utility functions for the application.
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with proper precedence.
 * Used extensively with shadcn/ui components.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date to a human-readable string.
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format a datetime to a human-readable string with time.
 */
export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Get relative time string (e.g., "2 hours ago").
 */
export function getRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffDay > 7) {
    return formatDate(d)
  } else if (diffDay > 0) {
    return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`
  } else if (diffHour > 0) {
    return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`
  } else if (diffMin > 0) {
    return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`
  } else {
    return 'Just now'
  }
}

/**
 * Truncate a string to a maximum length with ellipsis.
 */
export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength - 3) + '...'
}

/**
 * Format a number with commas (e.g., 1000 -> 1,000).
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US')
}

/**
 * Get severity color classes for badges.
 */
export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'bg-red-100 text-red-800 border-red-200'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200'
    case 'info':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200'
  }
}

/**
 * Get category color classes.
 */
export function getCategoryColor(category: string): string {
  switch (category.toLowerCase()) {
    case 'security':
      return 'bg-purple-100 text-purple-800'
    case 'quality':
      return 'bg-green-100 text-green-800'
    case 'complexity':
    case 'maintainability':
      return 'bg-orange-100 text-orange-800'
    case 'best-practices':
      return 'bg-cyan-100 text-cyan-800'
    case 'performance':
      return 'bg-pink-100 text-pink-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Get score color (for review overall scores).
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}
