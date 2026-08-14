export interface ClothingItem {
  id: string
  name: string
  category: string
  color: string
  swatch: string // CSS color used as a stand-in until real product photos exist
  price: number
  currency: string
  sizes: string[]
}
