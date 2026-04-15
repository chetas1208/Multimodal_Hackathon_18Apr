import { defineStore } from 'pinia'
import type { DashboardStats, Analysis } from '~/types'

function recentDates(days: number): { date: string; count: number }[] {
  const result: { date: string; count: number }[] = []
  const counts = [3, 7, 5, 12, 8, 15, 10]
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    result.push({
      date: d.toISOString().split('T')[0],
      count: counts[i % counts.length],
    })
  }
  return result
}

const mockStats: DashboardStats = {
  total_requests: 142,
  videos_generated: 87,
  clips_generated: 234,
  active_jobs: 3,
  failed_jobs: 5,
  avg_processing_time: 185,
  recent_activity: recentDates(7),
}

const mockAnalyses: Analysis[] = [
  {
    id: 'analysis-001',
    job_id: 'job-a1b2c3d4',
    asset_id: 'asset-001',
    hook_score: 82,
    cta_score: 71,
    pacing_score: 88,
    platform_fit_score: 91,
    engagement_score: 79,
    explanation: 'Strong opening hook with product reveal in first 2 seconds. Good pacing with dynamic cuts every 3-4 seconds. CTA could be more prominent — consider adding a text overlay for the offer. Platform fit is excellent for TikTok with vertical format and trending audio style.',
    clip_selection_reason: null,
    platform_recommendations: {
      tiktok: { score: 91, notes: 'Ideal format and pacing for TikTok audience' },
      instagram_reels: { score: 85, notes: 'Works well, consider adding branded intro' },
      youtube_shorts: { score: 72, notes: 'Could benefit from longer intro context' },
    },
    created_at: '2025-04-14T10:09:00Z',
  },
  {
    id: 'analysis-002',
    job_id: 'job-e5f6g7h8',
    asset_id: 'asset-003',
    hook_score: 68,
    cta_score: 55,
    pacing_score: 74,
    platform_fit_score: 80,
    engagement_score: 65,
    explanation: 'Clip opens with a decent hook but could be more attention-grabbing. The review segment is informative but pacing slows in the middle. No clear CTA present. Subtitles are well-timed and improve accessibility.',
    clip_selection_reason: 'Selected for highest engagement potential from source — features the key product comparison segment with strong viewer retention signals.',
    platform_recommendations: {
      tiktok: { score: 75, notes: 'Tighten pacing for TikTok audience' },
      instagram_reels: { score: 80, notes: 'Good fit with minor tweaks' },
    },
    created_at: '2025-04-14T11:26:00Z',
  },
  {
    id: 'analysis-003',
    job_id: 'job-e5f6g7h8',
    asset_id: 'asset-004',
    hook_score: 45,
    cta_score: 38,
    pacing_score: 52,
    platform_fit_score: 60,
    engagement_score: 42,
    explanation: 'This clip has a slower start which may lose viewers. The content is valuable but needs re-editing for short-form. Consider a pattern interrupt in the first second. CTA is completely absent.',
    clip_selection_reason: 'Contains the technical deep-dive segment — appeals to niche audience but lower general engagement potential.',
    platform_recommendations: {
      youtube_shorts: { score: 65, notes: 'Better suited for YouTube audience who expect more depth' },
    },
    created_at: '2025-04-14T11:26:05Z',
  },
]

export const useAnalyticsStore = defineStore('analytics', {
  state: () => ({
    stats: mockStats as DashboardStats,
    analyses: mockAnalyses as Analysis[],
    currentAnalysis: null as Analysis | null,
    loading: false,
  }),

  actions: {
    async fetchDashboardStats() {
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<DashboardStats>('/analytics/dashboard')
        this.stats = result
      } catch {
        // keep mock
      } finally {
        this.loading = false
      }
    },

    async fetchAnalysis(jobId: string) {
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<Analysis>(`/analytics/jobs/${jobId}`)
        this.currentAnalysis = result
      } catch {
        this.currentAnalysis = this.analyses.find((a) => a.job_id === jobId) || null
      } finally {
        this.loading = false
      }
    },

    getAnalysisForJob(jobId: string): Analysis | undefined {
      return this.analyses.find((a) => a.job_id === jobId)
    },

    getAnalysisForAsset(assetId: string): Analysis | undefined {
      return this.analyses.find((a) => a.asset_id === assetId)
    },
  },
})
