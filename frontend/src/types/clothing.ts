export interface ClothingListItem {
  id: string
  name: string
  brand: string | null
  category: string
  primary_color: string
  available_colors: string[]
  price: number
  currency: string
  fit_type: string | null
  available_sizes: string[]
}

export interface PaginatedClothing {
  items: ClothingListItem[]
  total: number
  page: number
  page_size: number
}
