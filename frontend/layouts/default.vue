<script setup lang="ts">
const sidebarOpen = ref(false)
</script>

<template>
  <div class="flex h-screen bg-zinc-950 text-zinc-100">
    <Sidebar :open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex flex-1 flex-col overflow-hidden">
      <AppHeader :sidebar-open="sidebarOpen" @toggle-sidebar="sidebarOpen = !sidebarOpen" />

      <main class="flex-1 overflow-y-auto">
        <div class="mx-auto max-w-7xl px-4 py-6 lg:px-8">
          <slot />
        </div>
      </main>
    </div>
  </div>
</template>
