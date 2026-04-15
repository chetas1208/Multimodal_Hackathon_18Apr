<script setup lang="ts">
defineProps<{
  sidebarOpen: boolean
}>()

const emit = defineEmits<{
  toggleSidebar: []
}>()

const apiHealthy = ref(true)
const searchQuery = ref('')

async function checkHealth() {
  try {
    const api = useApi()
    await api.request('/health')
    apiHealthy.value = true
  } catch {
    apiHealthy.value = false
  }
}

onMounted(() => {
  checkHealth()
  const interval = setInterval(checkHealth, 30000)
  onUnmounted(() => clearInterval(interval))
})
</script>

<template>
  <header class="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-zinc-800 bg-zinc-950/80 px-4 backdrop-blur-xl lg:px-6">
    <button
      class="rounded-lg p-2 text-zinc-400 hover:bg-zinc-800 hover:text-white lg:hidden"
      @click="emit('toggleSidebar')"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
      </svg>
    </button>

    <div class="flex flex-1 items-center gap-4">
      <div class="relative hidden w-72 sm:block">
        <svg class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search jobs, assets..."
          class="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 pl-10 pr-4 text-sm text-zinc-300 placeholder-zinc-500 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        />
      </div>
    </div>

    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2 rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5">
        <span
          class="h-2 w-2 rounded-full"
          :class="apiHealthy ? 'bg-emerald-400' : 'bg-red-400'"
        />
        <span class="text-xs text-zinc-400">
          {{ apiHealthy ? 'API Connected' : 'API Offline' }}
        </span>
      </div>
    </div>
  </header>
</template>
