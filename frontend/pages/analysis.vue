<script setup lang="ts">
const analyticsStore = useAnalyticsStore()
const jobsStore = useJobsStore()

const completedJobs = computed(() =>
  jobsStore.jobs.filter((j) => j.status === 'completed')
)

const selectedJobId = ref(completedJobs.value[0]?.id || '')

const currentAnalysis = computed(() => {
  if (!selectedJobId.value) return null
  return analyticsStore.analyses.find((a) => a.job_id === selectedJobId.value) || null
})

const averageScore = computed(() => {
  if (!currentAnalysis.value) return 0
  const a = currentAnalysis.value
  return Math.round((a.hook_score + a.cta_score + a.pacing_score + a.platform_fit_score + a.engagement_score) / 5)
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-2xl font-bold text-white">Analysis</h1>
      <p class="text-sm text-zinc-500">AI-powered video quality analysis and recommendations</p>
    </div>

    <!-- Job Selector -->
    <div class="flex flex-wrap items-center gap-3">
      <label class="text-sm text-zinc-400">Select Job:</label>
      <select
        v-model="selectedJobId"
        class="min-w-[260px] rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 outline-none focus:border-indigo-500"
      >
        <option value="" disabled>Choose a completed job</option>
        <option v-for="job in completedJobs" :key="job.id" :value="job.id">
          {{ job.id }} — {{ job.workflow_type === 'generate_video' ? 'Generate Video' : 'Clip Shorts' }}
        </option>
      </select>
    </div>

    <!-- No analysis state -->
    <div v-if="!currentAnalysis" class="py-16 text-center">
      <svg class="mx-auto h-14 w-14 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p class="mt-3 text-sm text-zinc-500">Select a completed job to view analysis</p>
    </div>

    <template v-else>
      <!-- Overall Score -->
      <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
        <div class="flex items-center gap-4">
          <div
            class="flex h-14 w-14 items-center justify-center rounded-xl text-xl font-bold"
            :class="{
              'bg-emerald-500/10 text-emerald-400': averageScore >= 70,
              'bg-amber-500/10 text-amber-400': averageScore >= 40 && averageScore < 70,
              'bg-red-500/10 text-red-400': averageScore < 40,
            }"
          >
            {{ averageScore }}
          </div>
          <div>
            <p class="text-lg font-semibold text-white">Overall Score</p>
            <p class="text-sm text-zinc-500">Average across all 5 dimensions</p>
          </div>
        </div>
      </div>

      <!-- Score Cards -->
      <div class="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
        <AnalysisScoreCard label="Hook Score" :score="currentAnalysis.hook_score" />
        <AnalysisScoreCard label="CTA Score" :score="currentAnalysis.cta_score" />
        <AnalysisScoreCard label="Pacing Score" :score="currentAnalysis.pacing_score" />
        <AnalysisScoreCard label="Platform Fit" :score="currentAnalysis.platform_fit_score" />
        <AnalysisScoreCard label="Engagement" :score="currentAnalysis.engagement_score" />
      </div>

      <!-- Radar Chart + Explanation -->
      <div class="grid gap-6 lg:grid-cols-2">
        <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
          <h3 class="mb-4 text-sm font-medium text-zinc-300">Score Breakdown</h3>
          <ScoreBreakdownChart :analysis="currentAnalysis" />
        </div>

        <div class="space-y-4">
          <!-- Explanation -->
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
            <h3 class="mb-3 text-sm font-medium text-zinc-300">Analysis Explanation</h3>
            <p class="text-sm leading-relaxed text-zinc-400">{{ currentAnalysis.explanation }}</p>
          </div>

          <!-- Clip Selection Reason -->
          <div v-if="currentAnalysis.clip_selection_reason" class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
            <h3 class="mb-3 text-sm font-medium text-zinc-300">Clip Selection Reason</h3>
            <p class="text-sm leading-relaxed text-zinc-400">{{ currentAnalysis.clip_selection_reason }}</p>
          </div>

          <!-- Platform Recommendations -->
          <div v-if="Object.keys(currentAnalysis.platform_recommendations).length" class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-5">
            <h3 class="mb-3 text-sm font-medium text-zinc-300">Platform Recommendations</h3>
            <div class="space-y-3">
              <div
                v-for="(rec, platform) in currentAnalysis.platform_recommendations"
                :key="platform"
                class="flex items-start gap-3 rounded-lg border border-zinc-800/50 p-3"
              >
                <div
                  class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-xs font-bold"
                  :class="{
                    'text-emerald-400': (rec as any).score >= 70,
                    'text-amber-400': (rec as any).score >= 40 && (rec as any).score < 70,
                    'text-red-400': (rec as any).score < 40,
                  }"
                >
                  {{ (rec as any).score }}
                </div>
                <div>
                  <p class="text-sm font-medium capitalize text-zinc-300">
                    {{ String(platform).replace('_', ' ') }}
                  </p>
                  <p class="text-xs text-zinc-500">{{ (rec as any).notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
