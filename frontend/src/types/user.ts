export interface User {
  id: string
  email: string
  email_verified: boolean
  is_admin: boolean
  is_guest: boolean
  created_at: string
}

export type MeasurementSystem = 'metric' | 'imperial'
export type FitPreference = 'slim' | 'regular' | 'relaxed' | 'oversized'
export type BodyShape =
  | 'rectangle'
  | 'triangle'
  | 'inverted_triangle'
  | 'hourglass'
  | 'oval'
  | 'not_sure'
export type ColorGroup = 'neutral' | 'dark' | 'light' | 'pastel' | 'bright'

export interface UserProfile {
  name: string | null
  age_range: string | null
  gender_preference: string | null
  country_region: string | null
  measurement_system: MeasurementSystem
  updated_at: string | null
}

export interface BodyMeasurement {
  height_cm: number | null
  weight_kg: number | null
  usual_shirt_size: string | null
  usual_pants_size: string | null
  usual_dress_size: string | null
  chest_cm: number | null
  waist_cm: number | null
  hip_cm: number | null
  shoulder_cm: number | null
  inseam_cm: number | null
  arm_length_cm: number | null
  leg_length_cm: number | null
  foot_size: number | null
  fit_preference: FitPreference | null
  body_shape: BodyShape | null
  ai_estimated: boolean
  updated_at: string | null
}

export interface StylePreference {
  favorite_colors: string[]
  color_group: ColorGroup | null
  styles: string[]
  occasions: string[]
  updated_at: string | null
}
