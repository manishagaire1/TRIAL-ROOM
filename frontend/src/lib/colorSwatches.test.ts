import { getColorHex } from './colorSwatches'

describe('getColorHex', () => {
  it('returns the known hex code for a catalog color', () => {
    expect(getColorHex('Navy')).toBe('#1e3a5f')
  })

  it('falls back to a neutral gray for an unknown color instead of throwing', () => {
    expect(getColorHex('Some Color Nobody Seeded')).toBe('#a3a3a3')
  })

  it('is case-sensitive to the exact catalog color name', () => {
    // Documents current behavior: lowercase "navy" is not in the map,
    // so it should fall back rather than silently matching "Navy".
    expect(getColorHex('navy')).toBe('#a3a3a3')
  })
})
