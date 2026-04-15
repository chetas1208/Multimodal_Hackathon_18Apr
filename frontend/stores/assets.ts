import { defineStore } from 'pinia'
import type { Asset, AssetType } from '~/types'

const mockAssets: Asset[] = [
  {
    id: 'asset-001',
    job_id: 'job-a1b2c3d4',
    user_id: 'user-001',
    asset_type: 'video',
    file_path: '/storage/videos/earbuds-showcase.mp4',
    file_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
    file_size: 15_400_000,
    duration: 32,
    metadata: { resolution: '1080x1920', fps: 30, codec: 'h264' },
    tags: ['product', 'earbuds', 'tiktok', 'showcase'],
    created_at: '2025-04-14T10:08:30Z',
  },
  {
    id: 'asset-002',
    job_id: 'job-a1b2c3d4',
    user_id: 'user-001',
    asset_type: 'thumbnail',
    file_path: '/storage/thumbs/earbuds-thumb.jpg',
    file_url: 'https://picsum.photos/seed/earbuds/400/700',
    file_size: 245_000,
    duration: null,
    metadata: { resolution: '400x700', format: 'jpeg' },
    tags: ['thumbnail', 'earbuds'],
    created_at: '2025-04-14T10:08:35Z',
  },
  {
    id: 'asset-003',
    job_id: 'job-e5f6g7h8',
    user_id: 'user-001',
    asset_type: 'video',
    file_path: '/storage/clips/review-clip1.mp4',
    file_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4',
    file_size: 8_200_000,
    duration: 28,
    metadata: { resolution: '1080x1920', fps: 30 },
    tags: ['clip', 'review', 'short'],
    created_at: '2025-04-14T11:25:10Z',
  },
  {
    id: 'asset-004',
    job_id: 'job-e5f6g7h8',
    user_id: 'user-001',
    asset_type: 'video',
    file_path: '/storage/clips/review-clip2.mp4',
    file_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4',
    file_size: 12_100_000,
    duration: 45,
    metadata: { resolution: '1080x1920', fps: 30 },
    tags: ['clip', 'review', 'highlight'],
    created_at: '2025-04-14T11:25:15Z',
  },
  {
    id: 'asset-005',
    job_id: 'job-e5f6g7h8',
    user_id: 'user-001',
    asset_type: 'subtitle',
    file_path: '/storage/subs/review-clip1.srt',
    file_url: '/storage/subs/review-clip1.srt',
    file_size: 3_400,
    duration: null,
    metadata: { format: 'srt', language: 'en' },
    tags: ['subtitle', 'english'],
    created_at: '2025-04-14T11:25:12Z',
  },
  {
    id: 'asset-006',
    job_id: 'job-a1b2c3d4',
    user_id: 'user-001',
    asset_type: 'image',
    file_path: '/storage/images/earbuds-promo.png',
    file_url: 'https://picsum.photos/seed/promo/400/700',
    file_size: 520_000,
    duration: null,
    metadata: { resolution: '1080x1920', format: 'png' },
    tags: ['promo', 'earbuds', 'marketing'],
    created_at: '2025-04-14T10:09:00Z',
  },
  {
    id: 'asset-007',
    job_id: 'job-e5f6g7h8',
    user_id: 'user-001',
    asset_type: 'thumbnail',
    file_path: '/storage/thumbs/clip1-thumb.jpg',
    file_url: 'https://picsum.photos/seed/clip1/400/700',
    file_size: 198_000,
    duration: null,
    metadata: { resolution: '400x700' },
    tags: ['thumbnail', 'clip'],
    created_at: '2025-04-14T11:25:18Z',
  },
  {
    id: 'asset-008',
    job_id: 'job-a1b2c3d4',
    user_id: 'user-001',
    asset_type: 'video',
    file_path: '/storage/videos/earbuds-ig-version.mp4',
    file_url: 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4',
    file_size: 18_700_000,
    duration: 30,
    metadata: { resolution: '1080x1080', fps: 30, platform: 'instagram' },
    tags: ['product', 'earbuds', 'instagram', 'square'],
    created_at: '2025-04-14T10:10:00Z',
  },
]

export const useAssetsStore = defineStore('assets', {
  state: () => ({
    assets: mockAssets as Asset[],
    loading: false,
    filterType: '' as AssetType | '',
  }),

  getters: {
    filteredAssets(state): Asset[] {
      if (!state.filterType) return state.assets
      return state.assets.filter((a) => a.asset_type === state.filterType)
    },
  },

  actions: {
    async fetchAssets(filters?: { asset_type?: AssetType }) {
      this.loading = true
      try {
        const api = useApi()
        const result = await api.request<Asset[]>('/assets', {
          method: 'GET',
          params: filters,
        })
        this.assets = result
      } catch {
        // keep mock data
      } finally {
        this.loading = false
      }
    },

    async deleteAsset(id: string) {
      try {
        const api = useApi()
        await api.request(`/assets/${id}`, { method: 'DELETE' })
      } catch {
        // proceed locally
      }
      this.assets = this.assets.filter((a) => a.id !== id)
    },
  },
})
