<template>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Monthly Trends</h3>
    <Bar v-if="chartData" :data="chartData" :options="chartOptions" class="max-h-56" />
    <p v-else class="text-sm text-center py-8">No data available</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend
} from 'chart.js'
import type { MonthlyTrend } from '@/types'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const props = defineProps<{ trends: MonthlyTrend[] }>()

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

const chartData = computed(() => {
  if (!props.trends.length) return null
  return {
    labels: props.trends.map(t => `${MONTHS[t.month - 1]} ${t.year}`),
    datasets: [
      {
        label: 'Income',
        data: props.trends.map(t => t.income),
        backgroundColor: '#22c55e',
        borderRadius: 6,
        borderSkipped: false,
      },
      {
        label: 'Expense',
        data: props.trends.map(t => t.expense),
        backgroundColor: '#f43f5e',
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { position: 'top' as const, labels: { font: { family: 'DM Sans' }, boxRadius: 4 } },
    tooltip: { callbacks: { label: (ctx: any) => ` ฿${ctx.parsed.y.toLocaleString()}` } },
  },
  scales: {
    x: { grid: { display: false }, ticks: { font: { family: 'DM Sans', size: 11 } } },
    y: {
      grid: { color: '#e2e8f0' },
      ticks: { font: { family: 'DM Sans', size: 11 }, callback: (v: any) => `฿${(v/1000).toFixed(0)}k` },
    },
  },
}
</script>
