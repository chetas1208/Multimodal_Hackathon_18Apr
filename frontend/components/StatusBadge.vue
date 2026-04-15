<script setup lang="ts">
import type { JobStatus } from '~/types'

const props = defineProps<{
  status: JobStatus | string
}>()

const config: Record<string, { color: string; label: string; pulse: boolean }> = {
  queued: { color: 'amber', label: 'Queued', pulse: false },
  processing: { color: 'blue', label: 'Processing', pulse: true },
  completed: { color: 'green', label: 'Completed', pulse: false },
  failed: { color: 'red', label: 'Failed', pulse: false },
}

const current = computed(() => config[props.status] || { color: 'gray', label: props.status, pulse: false })
</script>

<template>
  <span
    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium"
    :class="{
      'bg-amber-500/10 text-amber-400': current.color === 'amber',
      'bg-blue-500/10 text-blue-400': current.color === 'blue',
      'bg-green-500/10 text-green-400': current.color === 'green',
      'bg-red-500/10 text-red-400': current.color === 'red',
      'bg-gray-500/10 text-gray-400': current.color === 'gray',
    }"
  >
    <span
      class="h-1.5 w-1.5 rounded-full"
      :class="{
        'bg-amber-400': current.color === 'amber',
        'bg-blue-400': current.color === 'blue',
        'bg-green-400': current.color === 'green',
        'bg-red-400': current.color === 'red',
        'bg-gray-400': current.color === 'gray',
        'animate-pulse': current.pulse,
      }"
    />
    {{ current.label }}
  </span>
</template>
