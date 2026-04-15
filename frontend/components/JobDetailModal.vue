<script setup lang="ts">
import type { Job } from '~/types'

const props = defineProps<{
  job: Job | null
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

function getDuration(job: Job): string {
  if (!job.started_at) return 'Not started'
  const end = job.completed_at ? new Date(job.completed_at) : new Date()
  const start = new Date(job.started_at)
  const seconds = Math.round((end.getTime() - start.getTime()) / 1000)
  if (seconds < 60) return `${seconds} seconds`
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
}

function formatWorkflow(type: string): string {
  return type === 'generate_video' ? 'Generate Video' : 'Clip Shorts'
}

const timelineEvents = computed(() => {
  if (!props.job) return []
  const events = [
    { label: 'Created', time: props.job.created_at, active: true },
  ]
  if (props.job.started_at) {
    events.push({ label: 'Started', time: props.job.started_at, active: true })
  }
  if (props.job.completed_at) {
    events.push({
      label: props.job.status === 'failed' ? 'Failed' : 'Completed',
      time: props.job.completed_at,
      active: true,
    })
  }
  if (props.job.status === 'queued') {
    events.push({ label: 'Waiting in Queue', time: '', active: false })
  }
  if (props.job.status === 'processing') {
    events.push({ label: 'Processing...', time: '', active: false })
  }
  return events
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open && job"
      class="fixed inset-0 z-[60] flex items-start justify-end"
    >
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="emit('close')" />

      <div class="relative z-10 flex h-full w-full max-w-lg flex-col border-l border-zinc-800 bg-zinc-950 shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-zinc-800 px-6 py-4">
          <div>
            <h2 class="text-lg font-semibold text-white">Job Details</h2>
            <code class="text-xs text-zinc-500">{{ job.id }}</code>
          </div>
          <button
            class="rounded-lg p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white"
            @click="emit('close')"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto px-6 py-5 space-y-6">
          <!-- Status & Info -->
          <div class="grid grid-cols-2 gap-4">
            <div class="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
              <p class="mb-1 text-xs text-zinc-500">Status</p>
              <StatusBadge :status="job.status" />
            </div>
            <div class="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
              <p class="mb-1 text-xs text-zinc-500">Workflow</p>
              <p class="text-sm font-medium text-zinc-200">{{ formatWorkflow(job.workflow_type) }}</p>
            </div>
            <div class="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
              <p class="mb-1 text-xs text-zinc-500">Duration</p>
              <p class="text-sm font-medium text-zinc-200">{{ getDuration(job) }}</p>
            </div>
            <div class="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
              <p class="mb-1 text-xs text-zinc-500">User ID</p>
              <code class="text-xs text-zinc-400">{{ job.user_id }}</code>
            </div>
          </div>

          <!-- Timeline -->
          <div>
            <h3 class="mb-3 text-sm font-medium text-zinc-300">Timeline</h3>
            <div class="space-y-0">
              <div
                v-for="(event, i) in timelineEvents"
                :key="i"
                class="flex gap-3"
              >
                <div class="flex flex-col items-center">
                  <div
                    class="h-2.5 w-2.5 rounded-full border-2"
                    :class="event.active ? 'border-indigo-400 bg-indigo-400' : 'border-zinc-600 bg-zinc-900'"
                  />
                  <div
                    v-if="i < timelineEvents.length - 1"
                    class="w-px flex-1 bg-zinc-800"
                  />
                </div>
                <div class="pb-4">
                  <p class="text-sm font-medium" :class="event.active ? 'text-zinc-200' : 'text-zinc-500'">
                    {{ event.label }}
                  </p>
                  <p v-if="event.time" class="text-xs text-zinc-500">{{ formatDate(event.time) }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Error -->
          <div v-if="job.error_message" class="rounded-lg border border-red-500/20 bg-red-500/5 p-4">
            <p class="mb-1 text-xs font-medium text-red-400">Error</p>
            <p class="text-sm text-red-300">{{ job.error_message }}</p>
          </div>

          <!-- Input Data -->
          <div>
            <h3 class="mb-2 text-sm font-medium text-zinc-300">Input Data</h3>
            <pre class="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-xs text-zinc-400">{{ JSON.stringify(job.input_data, null, 2) }}</pre>
          </div>

          <!-- Output Data -->
          <div v-if="job.output_data">
            <h3 class="mb-2 text-sm font-medium text-zinc-300">Output Data</h3>
            <pre class="overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-xs text-zinc-400">{{ JSON.stringify(job.output_data, null, 2) }}</pre>
          </div>

          <!-- Dates -->
          <div class="space-y-2 text-xs text-zinc-500">
            <div class="flex justify-between">
              <span>Created</span>
              <span>{{ formatDate(job.created_at) }}</span>
            </div>
            <div class="flex justify-between">
              <span>Updated</span>
              <span>{{ formatDate(job.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
