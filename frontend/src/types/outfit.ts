export interface OutfitItem {
  clothing_id: string | null
  wardrobe_item_id: string | null
  source: 'catalog' | 'wardrobe'
  name: string
  category: string
  primary_color: string
  slot: string
}

export interface SavedOutfit {
  id: string
  name: string | null
  occasion: string | null
  liked: boolean
  created_at: string
  items: OutfitItem[]
}

export interface PaginatedOutfits {
  items: SavedOutfit[]
  total: number
  page: number
  page_size: number
}

export interface OutfitItemInput {
  clothing_id?: string
  wardrobe_item_id?: string
  slot?: string
}

export interface SavedOutfitCreate {
  name?: string
  occasion?: string
  clothing_id?: string
  items?: OutfitItemInput[]
}

export interface SavedOutfitUpdate {
  liked?: boolean
  name?: string
  occasion?: string
}

export interface OutfitComparisonEntry {
  outfit: SavedOutfit
  explanation: string
  is_strongest_match: boolean
}

export interface CompareResponse {
  entries: OutfitComparisonEntry[]
  summary: string
}
