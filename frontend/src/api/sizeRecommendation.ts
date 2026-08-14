import { apiClient } from '../lib/apiClient'
import type {
  SizeRecommendation,
  SizeRecommendationRequest,
} from '../types/sizeRecommendation'

export async function getSizeRecommendation(
  data: SizeRecommendationRequest,
): Promise<SizeRecommendation> {
  const { data: result } = await apiClient.post<SizeRecommendation>(
    '/size-recommendation',
    data,
  )
  return result
}
