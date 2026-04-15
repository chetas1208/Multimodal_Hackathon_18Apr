export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed'
export type WorkflowType = 'generate_video' | 'clip_shorts'
export type AssetType = 'video' | 'image' | 'subtitle' | 'thumbnail'

export interface User {
  id: string
  telegram_id: string
  username: string
  first_name: string
  created_at: string
}

export interface Job {
  id: string
  user_id: string
  workflow_type: WorkflowType
  status: JobStatus
  input_data: Record<string, any>
  output_data: Record<string, any> | null
  error_message: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface Asset {
  id: string
  job_id: string
  user_id: string
  asset_type: AssetType
  file_path: string
  file_url: string
  file_size: number
  duration: number | null
  metadata: Record<string, any>
  tags: string[]
  created_at: string
}

export interface Analysis {
  id: string
  job_id: string
  asset_id: string | null
  hook_score: number
  cta_score: number
  pacing_score: number
  platform_fit_score: number
  engagement_score: number
  explanation: string
  clip_selection_reason: string | null
  platform_recommendations: Record<string, any>
  created_at: string
}

export interface ActivityLog {
  id: string
  user_id: string | null
  job_id: string | null
  event_type: string
  message: string
  metadata: Record<string, any>
  level: 'info' | 'warning' | 'error'
  created_at: string
}

export interface DashboardStats {
  total_requests: number
  videos_generated: number
  clips_generated: number
  active_jobs: number
  failed_jobs: number
  avg_processing_time: number
  recent_activity: { date: string; count: number }[]
}
