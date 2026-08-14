// The backend stores color as a plain name (e.g. "Navy") — presentation
// concerns like hex codes for swatches stay on the frontend rather than
// polluting the catalog data model.
const COLOR_HEX: Record<string, string> = {
  Black: '#18181b',
  White: '#f5f5f4',
  Gray: '#71717a',
  Navy: '#1e3a5f',
  Blue: '#2563eb',
  Green: '#166534',
  Red: '#b91c1c',
  Pink: '#db2777',
  Purple: '#7e22ce',
  Brown: '#78350f',
  Beige: '#d6c7a1',
  Charcoal: '#3f3f46',
  Indigo: '#2c3e6b',
  Olive: '#4b5320',
  'Light Blue': '#93c5fd',
}

const FALLBACK_HEX = '#a3a3a3'

export function getColorHex(colorName: string): string {
  return COLOR_HEX[colorName] ?? FALLBACK_HEX
}
