<script setup lang="ts">
import { Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import type { Analysis } from '~/types'

ChartJS.register(RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend)

const props = defineProps<{
  analysis: Analysis
}>()

const chartData = computed(() => ({
  labels: ['Hook', 'CTA', 'Pacing', 'Platform Fit', 'Engagement'],
  datasets: [
    {
      label: 'Score',
      data: [
        props.analysis.hook_score,
        props.analysis.cta_score,
        props.analysis.pacing_score,
        props.analysis.platform_fit_score,
        props.analysis.engagement_score,
      ],
      backgroundColor: 'rgba(99, 102, 241, 0.15)',
      borderColor: 'rgba(99, 102, 241, 0.8)',
      borderWidth: 2,
      pointBackgroundColor: 'rgba(99, 102, 241, 1)',
      pointBorderColor: 'rgba(99, 102, 241, 1)',
      pointRadius: 4,
      pointHoverRadius: 6,
    },
  ],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#18181b',
      borderColor: '#3f3f46',
      borderWidth: 1,
      titleColor: '#e4e4e7',
      bodyColor: '#a1a1aa',
      padding: 12,
      cornerRadius: 8,
    },
  },
  scales: {
    r: {
      grid: { color: 'rgba(63, 63, 70, 0.3)' },
      angleLines: { color: 'rgba(63, 63, 70, 0.3)' },
      pointLabels: {
        color: '#a1a1aa',
        font: { size: 12 },
      },
      ticks: {
        display: false,
        stepSize: 20,
      },
      suggestedMin: 0,
      suggestedMax: 100,
    },
  },
}
</script>

<template>
  <div class="h-72">
    <Radar :data="chartData" :options="chartOptions" />
  </div>
</template>
