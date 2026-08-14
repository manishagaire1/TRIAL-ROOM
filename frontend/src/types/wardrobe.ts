export interface WardrobeItem {
  id: string
  category: string
  color: string
  label: string | null
  created_at: string
  image_url: string
}

export interface PaginatedWardrobe {
  items: WardrobeItem[]
  total: number
  page: number
  page_size: number
}
