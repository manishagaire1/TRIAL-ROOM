import { apiClient } from '../lib/apiClient'
import type { User } from '../types/user'

interface Credentials {
  email: string
  password: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export async function registerRequest(credentials: Credentials): Promise<User> {
  const { data } = await apiClient.post<User>('/auth/register', credentials)
  return data
}

export async function loginRequest(credentials: Credentials): Promise<string> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', credentials)
  return data.access_token
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await apiClient.get<User>('/users/me')
  return data
}
