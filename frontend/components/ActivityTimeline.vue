<script setup lang="ts">
import type { ActivityLog } from '~/types'

defineProps<{
  activities: ActivityLog[]
}>()

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function getRelativeTime(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

const eventTypeConfig: Record<string, { label: string; color: string }> = {
  'job.created': { label: 'Job Created', color: 'indigo' },
  'job.started': { label: 'Job Started', color: 'blue' },
  'job.completed': { label: 'Completed', color: 'emerald' },
  'job.failed': { label: 'Failed', color: 'red' },
  'system.health': { label: 'Health Check', color: 'green' },
  'system.warning': { label: 'Warning', color: 'amber' },
}

function getEventConfig(type: string) {
  return eventTypeConfig[type] || { label: type, color: 'gray' }
}

function getLevelDotColor(level: string): string {
  if (level === 'error') return 'bg-red-400'
  if (level === 'warning') return 'bg-amber-400'
  return 'bg-indigo-400'
}

function getLevelBorderColor(level: string): string {
  if (level === 'error') return 'border-red-500/20'
  if (level === 'warning') return 'border-amber-500/20'
  return 'border-zinc-800'
}
</script>

<template>
  <div class="space-y-0">
    <div
      v-for="(activity, i) in activities"
      :key="activity.id"
      class="flex gap-4"
    >
      <!-- Timeline line + dot -->
      <div class="flex flex-col items-center">
        <div
          class="mt-1.5 h-3 w-3 rounded-full border-2 border-zinc-900"
          :class="getLevelDotColor(activity.level)"
        />
        <div
          v-if="i < activities.length - 1"
          class="w-px flex-1 bg-zinc-800"
        />
      </div>

      <!-- Content -->
      <div class="min-w-0 flex-1 pb-6">
        <div
          class="rounded-lg border p-3 transition-colors"
          :class="getLevelBorderColor(activity.level)"
          :style="activity.level === 'error' ? 'background: rgba(239,68,68,0.03)' : activity.level === 'warning' ? 'background: rgba(245,158,11,0.03)' : ''"
        >
          <div class="mb-1 flex flex-wrap items-center gap-2">
            <span
              class="rounded px-1.5 py-0.5 text-[10px] font-medium"
              :class="{
                'bg-indigo-500/10 text-indigo-400': getEventConfig(activity.event_type).color === 'indigo',
                'bg-blue-500/10 text-blue-400': getEventConfig(activity.event_type).color === 'blue',
                'bg-emerald-500/10 text-emerald-400': getEventConfig(activity.event_type).color === 'emerald',
                'bg-red-500/10 text-red-400': getEventConfig(activity.event_type).color === 'red',
                'bg-green-500/10 text-green-400': getEventConfig(activity.event_type).color === 'green',
                'bg-amber-500/10 text-amber-400': getEventConfig(activity.event_type).color === 'amber',
                'bg-gray-500/10 text-gray-400': getEventConfig(activity.event_type).color === 'gray',
              }"
            >
              {{ getEventConfig(activity.event_type).label }}
            </span>
            <span v-if="activity.user_id" class="text-[10px] text-zinc-600">
              {{ activity.user_id }}
            </span>
            <span class="ml-auto text-[10px] text-zinc-600" :title="formatTime(activity.created_at)">
              {{ getRelativeTime(activity.created_at) }}
            </span>
          </div>
          <p class="text-sm" :class="activity.level === 'error' ? 'text-red-300' : activity.level === 'warning' ? 'text-amber-300' : 'text-zinc-300'">
            {{ activity.message }}
          </p>
          <p v-if="activity.job_id" class="mt-1 text-[10px] text-zinc-600">
            Job: {{ activity.job_id }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="activities.length === 0" class="py-12 text-center">
      <svg class="mx-auto h-10 w-10 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
        <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
      <p class="mt-2 text-sm text-zinc-500">No activity yet</p>
    </div>
  </div>
</template>
