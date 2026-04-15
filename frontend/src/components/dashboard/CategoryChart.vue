<template>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Expense Breakdown</h3>
    <div v-if="breakdown.length" class="flex items-center gap-6">
      <div class="w-36 h-36 flex-shrink-0">
        <Doughnut :data="chartData" :options="chartOptions" />
      </div>
      <div class="flex-1 space-y-2 min-w-0">
        <div
          v-for="(item, i) in breakdown.slice(0, 6)"
          :key="item.category_name"
          class="flex items-center gap-2 text-sm"
        >
          <span 
            class="w-2.5 h-2.5 rounded-full flex-shrink-0" 
            :style="{ background: item.category_color || '#cbd5e1' }" 
          />
          <span class="truncate flex-1">{{ item.category_name }}</span>
          <span class="font-mono flex-shrink-0">{{ item.percentage }}%</span>
        </div>
      </div>
    </div>
    <p v-else class="text-sm text-center py-8">No expense data</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js'
import type { CategoryBreakdown } from '@/types'

ChartJS.register(ArcElement, Tooltip)

const props = defineProps<{ breakdown: CategoryBreakdown[] }>()

const chartData = computed(() => ({
  labels: props.breakdown.map(b => b.category_name),
  datasets: [{
    data: props.breakdown.map(b => b.total),
    backgroundColor: props.breakdown.map(b => b.category_color || '#cbd5e1'),
    borderWidth: 0,
    hoverOffset: 4,
  }],
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  cutout: '70%',
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx: any) => ` ฿${ctx.parsed.toLocaleString()}` } },
  },
}
</script>
