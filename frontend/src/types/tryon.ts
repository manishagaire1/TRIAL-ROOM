export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface TryOnResult {
  image_url: string
  provider: string
  created_at: string
}

export interface TryOnJob {
  id: string
  status: JobStatus
  clothing_id: string
  clothing_name: string
  selected_size: string
  selected_color: string
  failure_reason: string | null
  created_at: string
  completed_at: string | null
  result: TryOnResult | null
}

export interface TryOnJobCreate {
  clothing_id: string
  selected_size: string
  selected_color: string
}

export interface PaginatedTryOnHistory {
  items: TryOnJob[]
  total: number
  page: number
  page_size: number
}
