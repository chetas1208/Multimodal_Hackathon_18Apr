<script setup lang="ts">
import type { Job, JobStatus, WorkflowType } from '~/types'

const jobsStore = useJobsStore()

const statusFilter = ref<JobStatus | ''>('')
const workflowFilter = ref<WorkflowType | ''>('')

watch([statusFilter, workflowFilter], () => {
  jobsStore.filters.status = statusFilter.value
  jobsStore.filters.workflow_type = workflowFilter.value
})

const selectedJob = ref<Job | null>(null)
const detailOpen = ref(false)

function onRowClick(job: Job) {
  selectedJob.value = job
  detailOpen.value = true
}

function onRetry(jobId: string) {
  jobsStore.retryJob(jobId)
}

function onDelete(jobId: string) {
  jobsStore.deleteJob(jobId)
  if (selectedJob.value?.id === jobId) {
    detailOpen.value = false
    selectedJob.value = null
  }
}

const currentPage = ref(1)
const pageSize = 10

const paginatedJobs = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return jobsStore.filteredJobs.slice(start, start + pageSize)
})

const totalPages = computed(() => Math.ceil(jobsStore.filteredJobs.length / pageSize))

const statusOptions = [
  { label: 'All Statuses', value: '' },
  { label: 'Queued', value: 'queued' },
  { label: 'Processing', value: 'processing' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
]

const workflowOptions = [
  { label: 'All Workflows', value: '' },
  { label: 'Generate Video', value: 'generate_video' },
  { label: 'Clip Shorts', value: 'clip_shorts' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Jobs</h1>
        <p class="text-sm text-zinc-500">Manage video generation and clipping jobs</p>
      </div>
      <div class="flex items-center gap-2 text-xs text-zinc-500">
        <span class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5">
          {{ jobsStore.filteredJobs.length }} jobs
        </span>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-3">
      <select
        v-model="statusFilter"
        class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 outline-none focus:border-indigo-500"
      >
        <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>

      <select
        v-model="workflowFilter"
        class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 outline-none focus:border-indigo-500"
      >
        <option v-for="opt in workflowOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </div>

    <!-- Table -->
    <JobsTable
      :jobs="paginatedJobs"
      :loading="jobsStore.loading"
      @row-click="onRowClick"
      @retry="onRetry"
      @delete="onDelete"
    />

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex items-center justify-between">
      <p class="text-xs text-zinc-500">
        Page {{ currentPage }} of {{ totalPages }}
      </p>
      <div class="flex gap-2">
        <button
          :disabled="currentPage <= 1"
          class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:bg-zinc-800 disabled:opacity-40"
          @click="currentPage--"
        >
          Previous
        </button>
        <button
          :disabled="currentPage >= totalPages"
          class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:bg-zinc-800 disabled:opacity-40"
          @click="currentPage++"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Detail Modal -->
    <JobDetailModal
      :job="selectedJob"
      :open="detailOpen"
      @close="detailOpen = false"
    />
  </div>
</template>
