<script setup lang="ts">
import type { Asset } from '~/types'

defineProps<{
  asset: Asset
}>()

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDuration(seconds: number | null): string {
  if (!seconds) return ''
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

const typeConfig: Record<string, { label: string; color: string }> = {
  video: { label: 'Video', color: 'indigo' },
  image: { label: 'Image', color: 'cyan' },
  subtitle: { label: 'Subtitle', color: 'amber' },
  thumbnail: { label: 'Thumbnail', color: 'violet' },
}

const isHovering = ref(false)
const videoRef = ref<HTMLVideoElement | null>(null)

watch(isHovering, (val) => {
  if (videoRef.value) {
    val ? videoRef.value.play() : videoRef.value.pause()
  }
})
</script>

<template>
  <div
    class="group overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900/50 transition-all hover:border-zinc-700 hover:shadow-lg hover:shadow-indigo-500/5"
    @mouseenter="isHovering = true"
    @mouseleave="isHovering = false"
  >
    <!-- Preview Area -->
    <div class="relative aspect-[9/16] max-h-64 w-full overflow-hidden bg-zinc-900">
      <video
        v-if="asset.asset_type === 'video'"
        ref="videoRef"
        :src="asset.file_url"
        class="h-full w-full object-cover"
        muted
        loop
        preload="metadata"
        playsinline
      />
      <img
        v-else-if="asset.asset_type === 'image' || asset.asset_type === 'thumbnail'"
        :src="asset.file_url"
        :alt="asset.file_path"
        class="h-full w-full object-cover"
      />
      <div
        v-else
        class="flex h-full items-center justify-center"
      >
        <svg class="h-12 w-12 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>

      <!-- Duration badge -->
      <span
        v-if="asset.duration"
        class="absolute bottom-2 right-2 rounded bg-black/70 px-1.5 py-0.5 text-[10px] font-medium text-white backdrop-blur-sm"
      >
        {{ formatDuration(asset.duration) }}
      </span>

      <!-- Type badge -->
      <span
        class="absolute left-2 top-2 rounded px-1.5 py-0.5 text-[10px] font-medium backdrop-blur-sm"
        :class="{
          'bg-indigo-500/20 text-indigo-300': typeConfig[asset.asset_type]?.color === 'indigo',
          'bg-cyan-500/20 text-cyan-300': typeConfig[asset.asset_type]?.color === 'cyan',
          'bg-amber-500/20 text-amber-300': typeConfig[asset.asset_type]?.color === 'amber',
          'bg-violet-500/20 text-violet-300': typeConfig[asset.asset_type]?.color === 'violet',
        }"
      >
        {{ typeConfig[asset.asset_type]?.label || asset.asset_type }}
      </span>

      <!-- Play icon overlay for video -->
      <div
        v-if="asset.asset_type === 'video' && !isHovering"
        class="absolute inset-0 flex items-center justify-center bg-black/20"
      >
        <div class="rounded-full bg-black/50 p-3 backdrop-blur-sm">
          <svg class="h-6 w-6 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Info Area -->
    <div class="p-3 space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs text-zinc-500">{{ formatSize(asset.file_size) }}</span>
        <span class="text-xs text-zinc-600">{{ formatDate(asset.created_at) }}</span>
      </div>

      <!-- Tags -->
      <div v-if="asset.tags.length" class="flex flex-wrap gap-1">
        <span
          v-for="tag in asset.tags.slice(0, 4)"
          :key="tag"
          class="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400"
        >
          {{ tag }}
        </span>
        <span v-if="asset.tags.length > 4" class="text-[10px] text-zinc-600">
          +{{ asset.tags.length - 4 }}
        </span>
      </div>

      <!-- Actions -->
      <div class="flex gap-2 pt-1">
        <a
          :href="asset.file_url"
          target="_blank"
          class="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:bg-zinc-700 hover:text-white"
        >
          <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Download
        </a>
      </div>
    </div>
  </div>
</template>
