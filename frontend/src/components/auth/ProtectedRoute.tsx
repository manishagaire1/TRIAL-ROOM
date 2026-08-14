import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  /** Section 24: history, saved outfits, and a persistent profile all
   * require a real account — a guest session (created silently by
   * Trial Room) isn't enough for these. */
  requireRealAccount?: boolean
}

export function ProtectedRoute({ children, requireRealAccount = false }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <p className="py-12 text-center text-sm text-neutral-500">Loading...</p>
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  if (requireRealAccount && user.is_guest) {
    return <Navigate to="/register" replace />
  }
  return <>{children}</>
}
