<script setup lang="ts">
const analyticsStore = useAnalyticsStore()
const jobsStore = useJobsStore()

const recentJobs = computed(() =>
  [...jobsStore.jobs]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
)
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex flex-col gap-1">
      <h1 class="text-2xl font-bold text-white">Dashboard</h1>
      <p class="text-sm text-zinc-500">Overview of your AI marketing studio activity</p>
    </div>

    <!-- Stats Cards -->
    <DashboardStats :stats="analyticsStore.stats" />

    <!-- Charts + Recent Jobs -->
    <div class="grid gap-6 lg:grid-cols-5">
      <!-- Activity Chart -->
      <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 lg:col-span-3">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-medium text-zinc-300">Jobs — Last 7 Days</h2>
          <span class="text-xs text-zinc-600">Updated just now</span>
        </div>
        <RecentActivityChart :data="analyticsStore.stats.recent_activity" />
      </div>

      <!-- Recent Jobs -->
      <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 lg:col-span-2">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-medium text-zinc-300">Recent Jobs</h2>
          <NuxtLink
            to="/jobs"
            class="text-xs text-indigo-400 hover:text-indigo-300"
          >
            View all
          </NuxtLink>
        </div>

        <div class="space-y-3">
          <div
            v-for="job in recentJobs"
            :key="job.id"
            class="flex items-center justify-between rounded-lg border border-zinc-800/50 p-3 transition-colors hover:bg-zinc-800/20"
          >
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <span class="text-sm text-zinc-300">
                  {{ job.workflow_type === 'generate_video' ? 'Generate Video' : 'Clip Shorts' }}
                </span>
              </div>
              <code class="text-[10px] text-zinc-600">{{ job.id }}</code>
            </div>
            <StatusBadge :status="job.status" />
          </div>

          <div v-if="recentJobs.length === 0" class="py-6 text-center text-sm text-zinc-600">
            No jobs yet
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="flex flex-wrap gap-3">
      <NuxtLink
        to="/jobs"
        class="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-300 transition-colors hover:bg-zinc-700 hover:text-white"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
        View All Jobs
      </NuxtLink>
      <NuxtLink
        to="/assets"
        class="inline-flex items-center gap-2 rounded-lg border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-300 transition-colors hover:bg-zinc-700 hover:text-white"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
        </svg>
        View Assets
      </NuxtLink>
      <NuxtLink
        to="/analysis"
        class="inline-flex items-center gap-2 rounded-lg border border-indigo-500/30 bg-indigo-600/10 px-4 py-2 text-sm font-medium text-indigo-400 transition-colors hover:bg-indigo-600/20"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        View Analysis
      </NuxtLink>
    </div>
  </div>
</template>
