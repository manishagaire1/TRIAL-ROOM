import { apiClient } from '../lib/apiClient'
import type {
  StyleRecommendation,
  StyleRecommendationRequest,
} from '../types/styleRecommendation'

export async function getStyleRecommendation(
  data: StyleRecommendationRequest,
): Promise<StyleRecommendation> {
  const { data: result } = await apiClient.post<StyleRecommendation>(
    '/style-recommendation',
    data,
  )
  return result
}
