import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import {
  fetchCurrentUser,
  guestSessionRequest,
  loginRequest,
  registerRequest,
} from '../api/auth'
import { getStoredToken, setStoredToken } from '../lib/apiClient'
import type { User } from '../types/user'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string) => Promise<void>
  logout: () => void
  /** Returns the current user, silently starting a guest session first
   * if nobody is logged in yet. Lets Trial Room stay zero-friction
   * (Section 24) while every action still has a real user to attach to. */
  ensureSession: () => Promise<User>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // On first load, if a token was saved from a previous session, use it
  // to fetch the current user instead of asking them to log in again.
  useEffect(() => {
    const token = getStoredToken()
    if (!token) {
      setIsLoading(false)
      return
    }
    fetchCurrentUser()
      .then(setUser)
      .catch(() => setStoredToken(null))
      .finally(() => setIsLoading(false))
  }, [])

  const login = async (email: string, password: string) => {
    const token = await loginRequest({ email, password })
    setStoredToken(token)
    setUser(await fetchCurrentUser())
  }

  const register = async (email: string, password: string) => {
    await registerRequest({ email, password })
    await login(email, password)
  }

  const logout = () => {
    setStoredToken(null)
    setUser(null)
  }

  const ensureSession = async (): Promise<User> => {
    if (user) return user
    const token = await guestSessionRequest()
    setStoredToken(token)
    const guestUser = await fetchCurrentUser()
    setUser(guestUser)
    return guestUser
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, register, logout, ensureSession }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
