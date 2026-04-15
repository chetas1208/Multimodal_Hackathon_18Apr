import { defineStore } from 'pinia'
import type { ActivityLog } from '~/types'

const mockActivities: ActivityLog[] = [
  {
    id: 'log-001',
    user_id: 'user-001',
    job_id: 'job-a1b2c3d4',
    event_type: 'job.created',
    message: 'New video generation job created via Telegram bot',
    metadata: { telegram_chat_id: '123456', command: '/generate' },
    level: 'info',
    created_at: '2025-04-14T10:04:45Z',
  },
  {
    id: 'log-002',
    user_id: 'user-001',
    job_id: 'job-a1b2c3d4',
    event_type: 'job.started',
    message: 'Video generation started — model: wan-2.1, resolution: 1080x1920',
    metadata: { model: 'wan-2.1' },
    level: 'info',
    created_at: '2025-04-14T10:05:00Z',
  },
  {
    id: 'log-003',
    user_id: 'user-001',
    job_id: 'job-a1b2c3d4',
    event_type: 'job.completed',
    message: 'Video generated successfully (32s, 15.4MB)',
    metadata: { duration: 32, file_size: 15400000 },
    level: 'info',
    created_at: '2025-04-14T10:08:30Z',
  },
  {
    id: 'log-004',
    user_id: 'user-001',
    job_id: 'job-e5f6g7h8',
    event_type: 'job.created',
    message: 'Clip extraction job created — source: long-form-review.mp4',
    metadata: { num_clips: 3 },
    level: 'info',
    created_at: '2025-04-14T11:19:30Z',
  },
  {
    id: 'log-005',
    user_id: 'user-001',
    job_id: 'job-e5f6g7h8',
    event_type: 'job.completed',
    message: '2 clips extracted from source video (28s + 45s)',
    metadata: { clips_count: 2 },
    level: 'info',
    created_at: '2025-04-14T11:25:15Z',
  },
  {
    id: 'log-006',
    user_id: 'user-002',
    job_id: 'job-i9j0k1l2',
    event_type: 'job.created',
    message: 'Summer sale video generation requested via Telegram',
    metadata: { platform: 'instagram_reels' },
    level: 'info',
    created_at: '2025-04-15T08:59:30Z',
  },
  {
    id: 'log-007',
    user_id: 'user-002',
    job_id: 'job-i9j0k1l2',
    event_type: 'job.started',
    message: 'Processing video generation for Instagram Reels format',
    metadata: {},
    level: 'info',
    created_at: '2025-04-15T09:00:00Z',
  },
  {
    id: 'log-008',
    user_id: 'user-003',
    job_id: 'job-m3n4o5p6',
    event_type: 'job.failed',
    message: 'Video generation failed — upstream model timeout after 300s',
    metadata: { error_code: 'TIMEOUT', retry_count: 0 },
    level: 'error',
    created_at: '2025-04-14T15:05:00Z',
  },
  {
    id: 'log-009',
    user_id: null,
    job_id: null,
    event_type: 'system.health',
    message: 'API health check passed — all services operational',
    metadata: { uptime: '48h 23m', memory_usage: '62%' },
    level: 'info',
    created_at: '2025-04-15T09:05:00Z',
  },
  {
    id: 'log-010',
    user_id: null,
    job_id: null,
    event_type: 'system.warning',
    message: 'GPU memory usage above 80% — queue processing may be slower',
    metadata: { gpu_memory: '82%' },
    level: 'warning',
    created_at: '2025-04-15T08:45:00Z',
  },
]

export const useActivityStore = defineStore('activity', {
  state: () => ({
    activities: mockActivities as ActivityLog[],
    loading: false,
    filterLevel: '' as ActivityLog['level'] | '',
    autoRefresh: false,
  }),

  getters: {
    filteredActivities(state): ActivityLog[] {
      if (!state.filterLevel) return state.activities
      return state.activities.filter((a) => a.level === state.filterLevel)
    },

    sortedActivities(): ActivityLog[] {
      return [...this.filteredActivities].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
    },
  },

  actions: {
    async fetchActivities(filters?: { level?: string }) {
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<ActivityLog[]>('/activity', {
          method: 'GET',
          params: filters,
        })
        this.activities = result
      } catch {
        // keep mock
      } finally {
        this.loading = false
      }
    },

    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
    },
  },
})
