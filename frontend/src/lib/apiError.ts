import axios from 'axios'

/**
 * Every backend error response is shaped { error: { code, message } }
 * (see backend/app/main.py). This pulls out a message safe to show a
 * user directly, falling back to something generic for anything
 * unexpected (network failure, etc.) instead of leaking raw error text.
 */
export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.error?.message
    if (typeof message === 'string') return message
  }
  return 'Something went wrong. Please try again.'
}
