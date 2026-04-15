<script setup lang="ts">
const props = defineProps<{
  label: string
  score: number
  icon?: string
}>()

const scoreColor = computed(() => {
  if (props.score >= 70) return 'emerald'
  if (props.score >= 40) return 'amber'
  return 'red'
})

const circumference = 2 * Math.PI * 36
const dashOffset = computed(() => circumference - (props.score / 100) * circumference)
</script>

<template>
  <div class="flex flex-col items-center rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition-colors hover:border-zinc-700">
    <!-- Circular Progress -->
    <div class="relative mb-3">
      <svg class="h-24 w-24 -rotate-90" viewBox="0 0 80 80">
        <circle
          cx="40"
          cy="40"
          r="36"
          fill="none"
          stroke="currentColor"
          stroke-width="4"
          class="text-zinc-800"
        />
        <circle
          cx="40"
          cy="40"
          r="36"
          fill="none"
          stroke-width="4"
          stroke-linecap="round"
          :stroke-dasharray="circumference"
          :stroke-dashoffset="dashOffset"
          class="transition-all duration-700 ease-out"
          :class="{
            'text-emerald-400': scoreColor === 'emerald',
            'text-amber-400': scoreColor === 'amber',
            'text-red-400': scoreColor === 'red',
          }"
          stroke="currentColor"
        />
      </svg>
      <div class="absolute inset-0 flex items-center justify-center">
        <span
          class="text-xl font-bold"
          :class="{
            'text-emerald-400': scoreColor === 'emerald',
            'text-amber-400': scoreColor === 'amber',
            'text-red-400': scoreColor === 'red',
          }"
        >
          {{ score }}
        </span>
      </div>
    </div>

    <p class="text-sm font-medium text-zinc-300">{{ label }}</p>
    <p class="mt-0.5 text-[10px] uppercase tracking-wider"
      :class="{
        'text-emerald-500': scoreColor === 'emerald',
        'text-amber-500': scoreColor === 'amber',
        'text-red-500': scoreColor === 'red',
      }"
    >
      {{ score >= 70 ? 'Good' : score >= 40 ? 'Average' : 'Needs Work' }}
    </p>
  </div>
</template>
