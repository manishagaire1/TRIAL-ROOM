import { useEffect, useState } from 'react'
import { apiClient } from '../lib/apiClient'

/**
 * Every image in this app is served through an authenticated,
 * ownership-checked route — never a public URL (docs/06). A plain
 * <img src="/api/..."> can't attach the Authorization header, so this
 * fetches the bytes through apiClient (which does attach it) and turns
 * them into a local blob: URL the <img> tag can use instead.
 */
export function useAuthedImageUrl(path: string | null): {
  url: string | null
  isLoading: boolean
} {
  const [url, setUrl] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!path) {
      setUrl(null)
      return
    }

    let objectUrl: string | null = null
    let cancelled = false
    setIsLoading(true)

    apiClient
      .get(path, { responseType: 'blob' })
      .then((response) => {
        if (cancelled) return
        objectUrl = URL.createObjectURL(response.data)
        setUrl(objectUrl)
      })
      .catch(() => {
        if (!cancelled) setUrl(null)
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })

    return () => {
      cancelled = true
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [path])

  return { url, isLoading }
}
