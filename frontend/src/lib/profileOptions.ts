// Option lists from docs/01 (Sections 7 & 8 of the original spec). Kept in
// one place so the measurements and style-preference forms stay in sync
// with each other and with the backend's Literal types.

export const FIT_PREFERENCES = [
  { value: 'slim', label: 'Slim' },
  { value: 'regular', label: 'Regular' },
  { value: 'relaxed', label: 'Relaxed' },
  { value: 'oversized', label: 'Oversized' },
] as const

export const BODY_SHAPES = [
  { value: 'rectangle', label: 'Rectangle' },
  { value: 'triangle', label: 'Triangle' },
  { value: 'inverted_triangle', label: 'Inverted triangle' },
  { value: 'hourglass', label: 'Hourglass' },
  { value: 'oval', label: 'Oval' },
  { value: 'not_sure', label: 'Not sure' },
] as const

export const COLOR_GROUPS = [
  { value: 'neutral', label: 'Neutral' },
  { value: 'dark', label: 'Dark' },
  { value: 'light', label: 'Light' },
  { value: 'pastel', label: 'Pastel' },
  { value: 'bright', label: 'Bright' },
] as const

export const FAVORITE_COLORS = [
  'Black',
  'White',
  'Gray',
  'Navy',
  'Blue',
  'Green',
  'Red',
  'Pink',
  'Purple',
  'Brown',
  'Beige',
  'Other',
]

export const STYLES = [
  'Casual',
  'Formal',
  'Business',
  'Business casual',
  'Streetwear',
  'Sporty',
  'Minimal',
  'Traditional',
  'Party',
  'Oversized',
]

export const OCCASIONS = [
  'Daily',
  'Work',
  'Interview',
  'Date',
  'Party',
  'Wedding',
  'Travel',
  'Exercise',
  'Other',
]
