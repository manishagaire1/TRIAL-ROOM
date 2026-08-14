import { apiClient } from '../lib/apiClient'
import type { PaginatedWardrobe, WardrobeItem } from '../types/wardrobe'

export async function getWardrobe(): Promise<PaginatedWardrobe> {
  const { data } = await apiClient.get<PaginatedWardrobe>('/wardrobe')
  return data
}

export async function uploadWardrobeItem(params: {
  file: File
  category: string
  color: string
  label?: string
}): Promise<WardrobeItem> {
  const formData = new FormData()
  formData.append('file', params.file)
  formData.append('category', params.category)
  formData.append('color', params.color)
  if (params.label) formData.append('label', params.label)
  const { data } = await apiClient.post<WardrobeItem>('/wardrobe', formData)
  return data
}

export async function deleteWardrobeItem(itemId: string): Promise<void> {
  await apiClient.delete(`/wardrobe/${itemId}`)
}
