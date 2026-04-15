<script setup lang="ts">
const activityStore = useActivityStore()

const filterLevel = ref<'info' | 'warning' | 'error' | ''>('')

watch(filterLevel, (val) => {
  activityStore.filterLevel = val
})

const levelOptions = [
  { label: 'All Levels', value: '' },
  { label: 'Info', value: 'info' },
  { label: 'Warning', value: 'warning' },
  { label: 'Error', value: 'error' },
]

let refreshInterval: ReturnType<typeof setInterval> | null = null

watch(() => activityStore.autoRefresh, (val) => {
  if (val) {
    refreshInterval = setInterval(() => {
      activityStore.fetchActivities()
    }, 5000)
  } else if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})

const errorCount = computed(() =>
  activityStore.activities.filter((a) => a.level === 'error').length
)
const warningCount = computed(() =>
  activityStore.activities.filter((a) => a.level === 'warning').length
)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-white">Bot Activity</h1>
        <p class="text-sm text-zinc-500">Real-time event log from the Telegram bot and processing pipeline</p>
      </div>
      <div class="flex items-center gap-3">
        <!-- Quick stats -->
        <span class="rounded-lg border border-red-500/20 bg-red-500/5 px-2.5 py-1 text-xs text-red-400">
          {{ errorCount }} errors
        </span>
        <span class="rounded-lg border border-amber-500/20 bg-amber-500/5 px-2.5 py-1 text-xs text-amber-400">
          {{ warningCount }} warnings
        </span>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex flex-wrap items-center gap-3">
      <select
        v-model="filterLevel"
        class="rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-2 text-sm text-zinc-300 outline-none focus:border-indigo-500"
      >
        <option v-for="opt in levelOptions" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>

      <button
        class="ml-auto flex items-center gap-2 rounded-lg border px-3 py-2 text-xs font-medium transition-colors"
        :class="activityStore.autoRefresh
          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
          : 'border-zinc-800 bg-zinc-900 text-zinc-400 hover:text-zinc-300'"
        @click="activityStore.toggleAutoRefresh()"
      >
        <span
          class="h-2 w-2 rounded-full"
          :class="activityStore.autoRefresh ? 'animate-pulse bg-emerald-400' : 'bg-zinc-600'"
        />
        {{ activityStore.autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF' }}
      </button>
    </div>

    <!-- Timeline -->
    <div class="rounded-xl border border-zinc-800 bg-zinc-900/30 p-5">
      <ActivityTimeline :activities="activityStore.sortedActivities" />
    </div>
  </div>
</template>
