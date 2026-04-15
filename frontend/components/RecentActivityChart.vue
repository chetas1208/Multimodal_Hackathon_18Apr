<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{
  data: { date: string; count: number }[]
}>()

const chartData = computed(() => ({
  labels: props.data.map((d) => {
    const date = new Date(d.date)
    return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })
  }),
  datasets: [
    {
      label: 'Jobs',
      data: props.data.map((d) => d.count),
      backgroundColor: 'rgba(99, 102, 241, 0.5)',
      borderColor: 'rgba(99, 102, 241, 1)',
      borderWidth: 1,
      borderRadius: 6,
      barThickness: 28,
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
    x: {
      grid: { display: false },
      ticks: { color: '#71717a', font: { size: 11 } },
      border: { display: false },
    },
    y: {
      grid: { color: 'rgba(63, 63, 70, 0.3)' },
      ticks: { color: '#71717a', font: { size: 11 }, stepSize: 5 },
      border: { display: false },
    },
  },
}
</script>

<template>
  <div class="h-64">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
