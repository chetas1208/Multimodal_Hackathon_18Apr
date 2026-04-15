<script setup lang="ts">
import type { DashboardStats } from '~/types'

defineProps<{
  stats: DashboardStats
}>()

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}m ${s}s`
}

const cards = computed(() => [
  {
    label: 'Total Requests',
    icon: 'M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
    color: 'indigo',
  },
  {
    label: 'Videos Generated',
    icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z',
    color: 'violet',
  },
  {
    label: 'Clips Generated',
    icon: 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z',
    color: 'cyan',
  },
  {
    label: 'Active Jobs',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
    color: 'emerald',
  },
  {
    label: 'Failed Jobs',
    icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z',
    color: 'red',
  },
  {
    label: 'Avg Process Time',
    icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
    color: 'amber',
  },
])
</script>

<template>
  <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
    <div
      v-for="(card, i) in cards"
      :key="card.label"
      class="group rounded-xl border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700"
    >
      <div class="mb-3 flex items-center justify-between">
        <div
          class="flex h-9 w-9 items-center justify-center rounded-lg"
          :class="{
            'bg-indigo-500/10': card.color === 'indigo',
            'bg-violet-500/10': card.color === 'violet',
            'bg-cyan-500/10': card.color === 'cyan',
            'bg-emerald-500/10': card.color === 'emerald',
            'bg-red-500/10': card.color === 'red',
            'bg-amber-500/10': card.color === 'amber',
          }"
        >
          <svg
            class="h-4 w-4"
            :class="{
              'text-indigo-400': card.color === 'indigo',
              'text-violet-400': card.color === 'violet',
              'text-cyan-400': card.color === 'cyan',
              'text-emerald-400': card.color === 'emerald',
              'text-red-400': card.color === 'red',
              'text-amber-400': card.color === 'amber',
            }"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            stroke-width="2"
          >
            <path stroke-linecap="round" stroke-linejoin="round" :d="card.icon" />
          </svg>
        </div>
      </div>
      <p class="text-2xl font-bold text-white">
        <template v-if="i === 0">{{ stats.total_requests.toLocaleString() }}</template>
        <template v-else-if="i === 1">{{ stats.videos_generated.toLocaleString() }}</template>
        <template v-else-if="i === 2">{{ stats.clips_generated.toLocaleString() }}</template>
        <template v-else-if="i === 3">{{ stats.active_jobs }}</template>
        <template v-else-if="i === 4">{{ stats.failed_jobs }}</template>
        <template v-else>{{ formatDuration(stats.avg_processing_time) }}</template>
      </p>
      <p class="mt-1 text-xs text-zinc-500">{{ card.label }}</p>
    </div>
  </div>
</template>
