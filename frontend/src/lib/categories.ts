// Mirrors backend/app/schemas/clothing.py's Category literal.
export const CATEGORIES = [
  'T-shirt',
  'Shirt',
  'Hoodie',
  'Sweater',
  'Jacket',
  'Coat',
  'Dress',
  'Skirt',
  'Jeans',
  'Pants',
  'Shorts',
  'Traditional clothing',
  'Shoes',
  'Accessories',
]

// Mirrors backend/app/services/slot_mapping.py — kept independent (like
// colorSwatches.ts) since one is Python and the other TypeScript.
const CATEGORY_SLOT: Record<string, string> = {
  'T-shirt': 'top',
  Shirt: 'top',
  Hoodie: 'top',
  Sweater: 'top',
  Jacket: 'outerwear',
  Coat: 'outerwear',
  Dress: 'dress',
  Jeans: 'bottom',
  Pants: 'bottom',
  Shorts: 'bottom',
  Skirt: 'bottom',
  Shoes: 'shoes',
  Accessories: 'accessory',
  'Traditional clothing': 'top',
}

export function slotForCategory(category: string): string {
  return CATEGORY_SLOT[category] ?? 'item'
}
