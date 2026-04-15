import { defineStore } from 'pinia'
import type { Job, JobStatus, WorkflowType } from '~/types'

interface JobFilters {
  status: JobStatus | ''
  workflow_type: WorkflowType | ''
}

const mockJobs: Job[] = [
  {
    id: 'job-a1b2c3d4',
    user_id: 'user-001',
    workflow_type: 'generate_video',
    status: 'completed',
    input_data: { prompt: 'Create a 30s product showcase for wireless earbuds', platform: 'tiktok', style: 'energetic' },
    output_data: { video_url: '/assets/demo-video-1.mp4', duration: 32, resolution: '1080x1920' },
    error_message: null,
    started_at: '2025-04-14T10:05:00Z',
    completed_at: '2025-04-14T10:08:30Z',
    created_at: '2025-04-14T10:04:45Z',
    updated_at: '2025-04-14T10:08:30Z',
  },
  {
    id: 'job-e5f6g7h8',
    user_id: 'user-001',
    workflow_type: 'clip_shorts',
    status: 'completed',
    input_data: { source_video: 'long-form-review.mp4', num_clips: 3, max_length: 60 },
    output_data: { clips: [{ url: '/clips/clip1.mp4', duration: 28 }, { url: '/clips/clip2.mp4', duration: 45 }] },
    error_message: null,
    started_at: '2025-04-14T11:20:00Z',
    completed_at: '2025-04-14T11:25:15Z',
    created_at: '2025-04-14T11:19:30Z',
    updated_at: '2025-04-14T11:25:15Z',
  },
  {
    id: 'job-i9j0k1l2',
    user_id: 'user-002',
    workflow_type: 'generate_video',
    status: 'processing',
    input_data: { prompt: 'Summer sale announcement for fashion brand', platform: 'instagram_reels', style: 'trendy' },
    output_data: null,
    error_message: null,
    started_at: '2025-04-15T09:00:00Z',
    completed_at: null,
    created_at: '2025-04-15T08:59:30Z',
    updated_at: '2025-04-15T09:00:00Z',
  },
  {
    id: 'job-m3n4o5p6',
    user_id: 'user-003',
    workflow_type: 'generate_video',
    status: 'failed',
    input_data: { prompt: 'Product unboxing video for headphones', platform: 'youtube_shorts' },
    output_data: null,
    error_message: 'Video generation timed out after 300s — upstream model unavailable',
    started_at: '2025-04-14T15:00:00Z',
    completed_at: '2025-04-14T15:05:00Z',
    created_at: '2025-04-14T14:59:00Z',
    updated_at: '2025-04-14T15:05:00Z',
  },
  {
    id: 'job-q7r8s9t0',
    user_id: 'user-001',
    workflow_type: 'clip_shorts',
    status: 'queued',
    input_data: { source_video: 'podcast-episode-42.mp4', num_clips: 5, max_length: 45 },
    output_data: null,
    error_message: null,
    started_at: null,
    completed_at: null,
    created_at: '2025-04-15T09:10:00Z',
    updated_at: '2025-04-15T09:10:00Z',
  },
]

export const useJobsStore = defineStore('jobs', {
  state: () => ({
    jobs: mockJobs as Job[],
    currentJob: null as Job | null,
    loading: false,
    filters: { status: '', workflow_type: '' } as JobFilters,
  }),

  getters: {
    filteredJobs(state): Job[] {
      return state.jobs.filter((job) => {
        if (state.filters.status && job.status !== state.filters.status) return false
        if (state.filters.workflow_type && job.workflow_type !== state.filters.workflow_type) return false
        return true
      })
    },
  },

  actions: {
    async fetchJobs(filters?: Partial<JobFilters>) {
      if (filters) Object.assign(this.filters, filters)
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<Job[]>('/jobs', {
          method: 'GET',
          params: {
            status: this.filters.status || undefined,
            workflow_type: this.filters.workflow_type || undefined,
          },
        })
        this.jobs = result
      } catch {
        // fallback to mock data already in state
      } finally {
        this.loading = false
      }
    },

    async fetchJob(id: string) {
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<Job>(`/jobs/${id}`)
        this.currentJob = result
      } catch {
        this.currentJob = this.jobs.find((j) => j.id === id) || null
      } finally {
        this.loading = false
      }
    },

    async createJob(data: { workflow_type: WorkflowType; input_data: Record<string, any> }) {
      try {
        const api = useApi()
        const result = await api.request<Job>('/jobs', { method: 'POST', body: data })
        this.jobs.unshift(result)
        return result
      } catch {
        return null
      }
    },

    async retryJob(id: string) {
      try {
        const api = useApi()
        const result = await api.request<Job>(`/jobs/${id}/retry`, { method: 'POST' })
        const idx = this.jobs.findIndex((j) => j.id === id)
        if (idx !== -1) this.jobs[idx] = result
        return result
      } catch {
        const idx = this.jobs.findIndex((j) => j.id === id)
        if (idx !== -1) this.jobs[idx] = { ...this.jobs[idx], status: 'queued', error_message: null }
        return null
      }
    },

    async deleteJob(id: string) {
      try {
        const api = useApi()
        await api.request(`/jobs/${id}`, { method: 'DELETE' })
      } catch {
        // proceed with local removal
      }
      this.jobs = this.jobs.filter((j) => j.id !== id)
    },
  },
})
