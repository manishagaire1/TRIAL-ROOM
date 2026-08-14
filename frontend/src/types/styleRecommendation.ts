export interface StyleSuggestion {
  clothing_id: string
  name: string
  category: string
  primary_color: string
  price: number
  currency: string
  slot: string
  reason: string
}

export interface StyleRecommendation {
  anchor_clothing_id: string
  anchor_name: string
  anchor_color: string
  occasion: string | null
  suggestions: StyleSuggestion[]
  note: string
}

export interface StyleRecommendationRequest {
  clothing_id: string
  occasion?: string
}
