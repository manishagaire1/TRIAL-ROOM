import { apiClient } from '../lib/apiClient'
import type { BodyMeasurement, StylePreference, UserProfile } from '../types/user'

export async function getProfile(): Promise<UserProfile> {
  const { data } = await apiClient.get<UserProfile>('/users/profile')
  return data
}

export async function updateProfile(
  patch: Partial<UserProfile>,
): Promise<UserProfile> {
  const { data } = await apiClient.put<UserProfile>('/users/profile', patch)
  return data
}

export async function getMeasurements(): Promise<BodyMeasurement> {
  const { data } = await apiClient.get<BodyMeasurement>('/body-measurements')
  return data
}

export async function updateMeasurements(
  patch: Partial<BodyMeasurement>,
): Promise<BodyMeasurement> {
  const { data } = await apiClient.put<BodyMeasurement>('/body-measurements', patch)
  return data
}

export async function getStylePreferences(): Promise<StylePreference> {
  const { data } = await apiClient.get<StylePreference>('/style-preferences')
  return data
}

export async function updateStylePreferences(
  patch: Partial<StylePreference>,
): Promise<StylePreference> {
  const { data } = await apiClient.put<StylePreference>('/style-preferences', patch)
  return data
}
