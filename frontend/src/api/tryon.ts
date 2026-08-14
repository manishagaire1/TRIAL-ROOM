import { apiClient } from '../lib/apiClient'
import type { PaginatedTryOnHistory, TryOnJob, TryOnJobCreate } from '../types/tryon'

export async function createTryOnJob(data: TryOnJobCreate): Promise<TryOnJob> {
  const { data: job } = await apiClient.post<TryOnJob>('/tryon', data)
  return job
}

export async function getTryOnJob(jobId: string): Promise<TryOnJob> {
  const { data } = await apiClient.get<TryOnJob>(`/tryon/${jobId}`)
  return data
}

export async function getTryOnHistory(): Promise<PaginatedTryOnHistory> {
  const { data } = await apiClient.get<PaginatedTryOnHistory>('/tryon/history')
  return data
}

export async function deleteTryOnJob(jobId: string): Promise<void> {
  await apiClient.delete(`/tryon/${jobId}`)
}
