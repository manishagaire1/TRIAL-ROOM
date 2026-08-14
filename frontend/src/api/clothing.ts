import { apiClient } from '../lib/apiClient'
import type { PaginatedClothing } from '../types/clothing'

export async function getClothes(): Promise<PaginatedClothing> {
  const { data } = await apiClient.get<PaginatedClothing>('/clothes')
  return data
}
