<template>
  <div class="p-12 space-y-6 max-w-6xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">Dashboard</h1>
      <!-- Date filter -->
      <div class="flex items-center gap-2">
        <select v-model="period" @change="loadDashboard"
          class="input w-auto py-2 pr-8">
          <option value="month">This Month</option>
          <option value="quarter">This Quarter</option>
          <option value="year">This Year</option>
          <option value="all">All Time</option>
        </select>
      </div>
    </div>

    <!-- Stat cards -->
    <div v-if="dashboard" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        label="Total Income" :value="dashboard.period_summary.total_income"
        :icon="ArrowTrendingUpIcon" variant="income"
      />
      <StatCard
        label="Total Expense" :value="dashboard.period_summary.total_expense"
        :icon="ArrowTrendingDownIcon" variant="expense"
      />
      <StatCard
        label="Net Balance" :value="dashboard.period_summary.net"
        :icon="BanknotesIcon" variant="net"
      />
      <StatCard
        label="Transactions" :value="dashboard.period_summary.record_count"
        :icon="DocumentTextIcon" variant="neutral"
        currency=""
      />
    </div>

    <!-- Skeleton -->
    <div v-else-if="loading" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="card p-5 h-24 animate-pulse bg-slate-50" />
    </div>

    <!-- Charts row -->
    <div v-if="dashboard" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <TrendChart :trends="dashboard.monthly_trends" />
      <CategoryChart :breakdown="dashboard.category_breakdown" />
    </div>

    <!-- Recent Records -->
    <div v-if="dashboard?.recent_records.length" class="card p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-semibold">Recent Records</h3>
        <RouterLink :to="{ name: 'Records' }" class="text-xs font-medium">
          View all →
        </RouterLink>
      </div>
      <RecordRow
        v-for="r in dashboard.recent_records" :key="r.id"
        :record="r" :read-only="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, BanknotesIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useRecordsStore } from '@/stores/records'
import StatCard from '@/components/dashboard/StatCard.vue'
import TrendChart from '@/components/dashboard/TrendChart.vue'
import CategoryChart from '@/components/dashboard/CategoryChart.vue'
import RecordRow from '@/components/records/RecordRow.vue'
import { storeToRefs } from 'pinia'
import { startOfMonth, startOfQuarter, startOfYear, format } from 'date-fns'

const authStore = useAuthStore()
const recordsStore = useRecordsStore()
const { dashboard, loading } = storeToRefs(recordsStore)
const period = ref<'month' | 'quarter' | 'year' | 'all'>('month')

recordsStore.mockRecords()

function getDateRange() {
  const now = new Date()
  const map = {
    month: startOfMonth(now),
    quarter: startOfQuarter(now),
    year: startOfYear(now),
    all: null,
  }
  const from = map[period.value]
  return {
    date_from: from ? format(from, "yyyy-MM-dd'T'HH:mm:ss") : undefined,
    date_to: format(now, "yyyy-MM-dd'T'HH:mm:ss"),
  }
}

async function loadDashboard() {
  await recordsStore.fetchPersonalDashboard(getDateRange())
}

onMounted(loadDashboard)
</script>
