import { apiClient } from '../lib/apiClient'
import type {
  CompareResponse,
  PaginatedOutfits,
  SavedOutfit,
  SavedOutfitCreate,
  SavedOutfitUpdate,
} from '../types/outfit'

export async function createOutfit(data: SavedOutfitCreate): Promise<SavedOutfit> {
  const { data: outfit } = await apiClient.post<SavedOutfit>('/outfits', data)
  return outfit
}

export async function getOutfits(): Promise<PaginatedOutfits> {
  const { data } = await apiClient.get<PaginatedOutfits>('/outfits')
  return data
}

export async function updateOutfit(
  outfitId: string,
  data: SavedOutfitUpdate,
): Promise<SavedOutfit> {
  const { data: outfit } = await apiClient.patch<SavedOutfit>(`/outfits/${outfitId}`, data)
  return outfit
}

export async function deleteOutfit(outfitId: string): Promise<void> {
  await apiClient.delete(`/outfits/${outfitId}`)
}

export async function compareOutfits(
  outfitIds: string[],
  occasion?: string,
): Promise<CompareResponse> {
  const { data } = await apiClient.post<CompareResponse>('/outfits/compare', {
    outfit_ids: outfitIds,
    occasion,
  })
  return data
}
