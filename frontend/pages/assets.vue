<script setup lang="ts">
import type { AssetType } from '~/types'

const assetsStore = useAssetsStore()

const viewMode = ref<'grid' | 'list'>('grid')
const filterType = ref<AssetType | ''>('')

watch(filterType, (val) => {
  assetsStore.filterType = val
})

const typeOptions = [
  { label: 'All Types', value: '' },
  { label: 'Video', value: 'video' },
  { label: 'Image', value: 'image' },
  { label: 'Subtitle', value: 'subtitle' },
  { label: 'Thumbnail', value: 'thumbnail' },
]

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return '—'
  if (seconds < 60) return `${seconds}s`
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const typeColorMap: Record<string, string> = {
  video: 'bg-indigo-500/10 text-indigo-400',
  image: 'bg-cyan-500/10 text-cyan-400',
  subtitle: 'bg-amber-500/10 text-amber-400',
  thumbnail: 'bg-violet-500/10 text-violet-400',
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Assets</h1>
        <p class="text-sm text-zinc-500">Generated videos, images, thumbnails and subtitles</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-zinc-500">{{ assetsStore.filteredAssets.length }} assets</span>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-3">
      <select
        v-model="filterType"
        class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 outline-none focus:border-indigo-500"
      >
        <option v-for="opt in typeOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>

      <div class="ml-auto flex rounded-lg border border-zinc-800">
        <button
          class="rounded-l-lg px-3 py-2 text-xs transition-colors"
          :class="viewMode === 'grid' ? 'bg-zinc-700 text-white' : 'text-zinc-500 hover:text-zinc-300'"
          @click="viewMode = 'grid'"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
        </button>
        <button
          class="rounded-r-lg px-3 py-2 text-xs transition-colors"
          :class="viewMode === 'list' ? 'bg-zinc-700 text-white' : 'text-zinc-500 hover:text-zinc-300'"
          @click="viewMode = 'list'"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Grid View -->
    <AssetGrid v-if="viewMode === 'grid'" :assets="assetsStore.filteredAssets" />

    <!-- List View -->
    <div v-else class="overflow-hidden rounded-xl border border-zinc-800">
      <table class="w-full">
        <thead>
          <tr class="border-b border-zinc-800 bg-zinc-900/80">
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Asset</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Type</th>
            <th class="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500 md:table-cell">Size</th>
            <th class="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500 lg:table-cell">Duration</th>
            <th class="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500 md:table-cell">Created</th>
            <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Tags</th>
            <th class="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-zinc-500">Action</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-zinc-800/50">
          <tr
            v-for="asset in assetsStore.filteredAssets"
            :key="asset.id"
            class="transition-colors hover:bg-zinc-800/30"
          >
            <td class="px-4 py-3">
              <code class="text-xs text-zinc-400">{{ asset.id }}</code>
            </td>
            <td class="px-4 py-3">
              <span class="rounded px-1.5 py-0.5 text-[10px] font-medium" :class="typeColorMap[asset.asset_type]">
                {{ asset.asset_type }}
              </span>
            </td>
            <td class="hidden px-4 py-3 text-sm text-zinc-400 md:table-cell">
              {{ formatSize(asset.file_size) }}
            </td>
            <td class="hidden px-4 py-3 text-sm text-zinc-400 lg:table-cell">
              {{ formatDuration(asset.duration) }}
            </td>
            <td class="hidden px-4 py-3 text-sm text-zinc-400 md:table-cell">
              {{ formatDate(asset.created_at) }}
            </td>
            <td class="px-4 py-3">
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="tag in asset.tags.slice(0, 3)"
                  :key="tag"
                  class="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-500"
                >
                  {{ tag }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3 text-right">
              <a
                :href="asset.file_url"
                target="_blank"
                class="rounded-md p-1.5 text-zinc-500 hover:text-indigo-400"
              >
                <svg class="inline h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
              </a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
