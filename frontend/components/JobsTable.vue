<script setup lang="ts">
import type { Job } from '~/types'

defineProps<{
  jobs: Job[]
  loading: boolean
}>()

const emit = defineEmits<{
  rowClick: [job: Job]
  retry: [jobId: string]
  delete: [jobId: string]
}>()

function truncateId(id: string): string {
  return id.length > 12 ? id.slice(0, 12) + '...' : id
}

function formatWorkflow(type: string): string {
  return type === 'generate_video' ? 'Generate Video' : 'Clip Shorts'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getDuration(job: Job): string {
  if (!job.started_at) return '—'
  const end = job.completed_at ? new Date(job.completed_at) : new Date()
  const start = new Date(job.started_at)
  const seconds = Math.round((end.getTime() - start.getTime()) / 1000)
  if (seconds < 60) return `${seconds}s`
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
}
</script>

<template>
  <div class="overflow-hidden rounded-xl border border-zinc-800">
    <div v-if="loading" class="flex items-center justify-center py-12">
      <svg class="h-6 w-6 animate-spin text-indigo-400" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
    </div>

    <table v-else class="w-full">
      <thead>
        <tr class="border-b border-zinc-800 bg-zinc-900/80">
          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">ID</th>
          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Workflow</th>
          <th class="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500">Status</th>
          <th class="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500 md:table-cell">Created</th>
          <th class="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-500 lg:table-cell">Duration</th>
          <th class="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-zinc-500">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-zinc-800/50">
        <tr
          v-for="job in jobs"
          :key="job.id"
          class="cursor-pointer transition-colors hover:bg-zinc-800/30"
          @click="emit('rowClick', job)"
        >
          <td class="px-4 py-3">
            <code class="text-xs text-zinc-400">{{ truncateId(job.id) }}</code>
          </td>
          <td class="px-4 py-3">
            <span class="inline-flex items-center gap-1.5 text-sm text-zinc-300">
              <svg class="h-3.5 w-3.5 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  :d="job.workflow_type === 'generate_video'
                    ? 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z'
                    : 'M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z'"
                />
              </svg>
              {{ formatWorkflow(job.workflow_type) }}
            </span>
          </td>
          <td class="px-4 py-3">
            <StatusBadge :status="job.status" />
          </td>
          <td class="hidden px-4 py-3 text-sm text-zinc-400 md:table-cell">
            {{ formatDate(job.created_at) }}
          </td>
          <td class="hidden px-4 py-3 text-sm text-zinc-400 lg:table-cell">
            {{ getDuration(job) }}
          </td>
          <td class="px-4 py-3 text-right" @click.stop>
            <div class="flex items-center justify-end gap-1">
              <button
                v-if="job.status === 'failed'"
                class="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-amber-400"
                title="Retry"
                @click="emit('retry', job.id)"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                class="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-red-400"
                title="Delete"
                @click="emit('delete', job.id)"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="jobs.length === 0">
          <td colspan="6" class="px-4 py-12 text-center text-sm text-zinc-500">
            No jobs found
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
