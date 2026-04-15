<script setup lang="ts">
defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const route = useRoute()

const navItems = [
  { label: 'Dashboard', to: '/', icon: 'home' },
  { label: 'Jobs', to: '/jobs', icon: 'briefcase' },
  { label: 'Assets', to: '/assets', icon: 'film' },
  { label: 'Analysis', to: '/analysis', icon: 'chart-bar' },
  { label: 'Bot Activity', to: '/activity', icon: 'activity' },
  { label: 'Settings', to: '/settings', icon: 'settings' },
]

const iconPaths: Record<string, string> = {
  home: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1',
  briefcase: 'M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z',
  film: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z',
  'chart-bar': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  activity: 'M13 10V3L4 14h7v7l9-11h-7z',
  settings: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
}

function isActive(to: string) {
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}
</script>

<template>
  <!-- Mobile overlay -->
  <div
    v-if="open"
    class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
    @click="emit('close')"
  />

  <aside
    class="fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-zinc-800 bg-zinc-950 transition-transform duration-300 lg:static lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <!-- Brand -->
    <div class="flex h-16 items-center gap-3 border-b border-zinc-800 px-5">
      <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
        <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <h1 class="text-sm font-semibold text-white">Marketing Studio</h1>
        <p class="text-[10px] text-zinc-500">AI Video Platform</p>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
      <NuxtLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
        :class="isActive(item.to)
          ? 'bg-indigo-600/10 text-indigo-400'
          : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'"
        @click="emit('close')"
      >
        <svg class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round" :d="iconPaths[item.icon]" />
        </svg>
        {{ item.label }}
        <span
          v-if="isActive(item.to)"
          class="ml-auto h-1.5 w-1.5 rounded-full bg-indigo-400"
        />
      </NuxtLink>
    </nav>

    <!-- Footer -->
    <div class="border-t border-zinc-800 px-5 py-4">
      <p class="text-[10px] text-zinc-600">Marketing Studio v1.0.0</p>
      <p class="text-[10px] text-zinc-700">Hackathon Build</p>
    </div>
  </aside>
</template>
