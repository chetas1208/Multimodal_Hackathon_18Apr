<script setup lang="ts">
import type { Asset } from '~/types'

defineProps<{
  assets: Asset[]
}>()
</script>

<template>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
    <AssetCard
      v-for="asset in assets"
      :key="asset.id"
      :asset="asset"
    />
  </div>
  <div v-if="assets.length === 0" class="py-16 text-center">
    <svg class="mx-auto h-12 w-12 text-zinc-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
      <path stroke-linecap="round" stroke-linejoin="round" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
    </svg>
    <p class="mt-3 text-sm text-zinc-500">No assets found</p>
  </div>
</template>
