import { apiClient } from '../lib/apiClient'
import type { UserPhotoStatus } from '../types/photo'

export async function getPhotoStatus(): Promise<UserPhotoStatus> {
  const { data } = await apiClient.get<UserPhotoStatus>('/users/photo')
  return data
}

export async function uploadPhoto(file: File): Promise<UserPhotoStatus> {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await apiClient.post<UserPhotoStatus>('/users/photo', formData)
  return data
}

export async function deletePhoto(): Promise<void> {
  await apiClient.delete('/users/photo')
}
