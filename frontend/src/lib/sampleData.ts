import type { ClothingItem } from '../types/clothing'

/**
 * Static placeholder data so Phase 3 pages have something real to render.
 * This is clearly local sample data, not a fake AI or backend response —
 * every place it's used is labeled "Sample data" in the UI. It gets
 * replaced by real API calls starting in Phase 4 (auth) and Phase 6
 * (clothing catalog).
 */
export const sampleClothing: ClothingItem[] = [
  {
    id: 'c1',
    name: 'Classic Oxford Shirt',
    category: 'Shirt',
    color: 'Navy',
    swatch: '#1e3a5f',
    price: 42,
    currency: 'USD',
    sizes: ['S', 'M', 'L', 'XL'],
  },
  {
    id: 'c2',
    name: 'Everyday Hoodie',
    category: 'Hoodie',
    color: 'Charcoal',
    swatch: '#3f3f46',
    price: 58,
    currency: 'USD',
    sizes: ['S', 'M', 'L', 'XL'],
  },
  {
    id: 'c3',
    name: 'Straight-Fit Jeans',
    category: 'Jeans',
    color: 'Indigo',
    swatch: '#2c3e6b',
    price: 65,
    currency: 'USD',
    sizes: ['28', '30', '32', '34', '36'],
  },
  {
    id: 'c4',
    name: 'Minimal Bomber Jacket',
    category: 'Jacket',
    color: 'Olive',
    swatch: '#4b5320',
    price: 89,
    currency: 'USD',
    sizes: ['S', 'M', 'L'],
  },
]

export const sampleDashboardStats = {
  profileCompletionPercent: 40,
  recentTryOnsCount: 0,
  savedOutfitsCount: 0,
  shoppingListCount: 0,
}
