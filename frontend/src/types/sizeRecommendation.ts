export type Confidence = 'low' | 'medium' | 'high'

export interface SizeRecommendation {
  recommended_size: string | null
  alternative_size: string | null
  estimated_fit: string | null
  confidence: Confidence
  explanation: string
}

export interface SizeRecommendationRequest {
  clothing_id: string
  fit_preference?: string
}
