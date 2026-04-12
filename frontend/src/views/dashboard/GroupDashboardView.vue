<template>
  <div class="p-6 space-y-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between">
      <div>
        <RouterLink :to="{ name: 'Groups' }" class="text-xs text-ink-400 hover:text-ink-600 mb-1 inline-block">← Groups</RouterLink>
        <h1 class="font-display text-2xl font-bold text-ink-900">{{ group?.name }}</h1>
      </div>
      <div class="flex gap-2">
        <RouterLink :to="{ name: 'GroupDetail', params: { id } }" class="btn-ghost text-sm">Members</RouterLink>
        <RouterLink :to="{ name: 'GroupRecords', params: { id } }" class="btn-ghost text-sm">Records</RouterLink>
      </div>
    </div>

    <div v-if="dashboard" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Total Income" :value="dashboard.period_summary.total_income" :icon="ArrowTrendingUpIcon" variant="income" />
      <StatCard label="Total Expense" :value="dashboard.period_summary.total_expense" :icon="ArrowTrendingDownIcon" variant="expense" />
      <StatCard label="Net Balance" :value="dashboard.period_summary.net" :icon="BanknotesIcon" variant="net" />
      <StatCard label="Transactions" :value="dashboard.period_summary.record_count" :icon="DocumentTextIcon" variant="neutral" currency="" />
    </div>

    <div v-if="dashboard" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <TrendChart :trends="dashboard.monthly_trends" />
      <CategoryChart :breakdown="dashboard.category_breakdown" />
    </div>

    <div v-if="dashboard?.recent_records.length" class="card p-5">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-display text-base font-semibold text-ink-800">Recent Records</h3>
        <RouterLink :to="{ name: 'GroupRecords', params: { id } }" class="text-xs text-ink-400 hover:text-ink-600 font-medium">View all →</RouterLink>
      </div>
      <RecordRow v-for="r in dashboard.recent_records" :key="r.id" :record="r" :read-only="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, BanknotesIcon, DocumentTextIcon } from '@heroicons/vue/24/outline'
import { useRecordsStore } from '@/stores/records'
import { useGroupsStore } from '@/stores/groups'
import { storeToRefs } from 'pinia'
import StatCard from '@/components/dashboard/StatCard.vue'
import TrendChart from '@/components/dashboard/TrendChart.vue'
import CategoryChart from '@/components/dashboard/CategoryChart.vue'
import RecordRow from '@/components/records/RecordRow.vue'

const route = useRoute()
const id = route.params.id as string
const recordsStore = useRecordsStore()
const groupsStore = useGroupsStore()
const { dashboard } = storeToRefs(recordsStore)
const { currentGroup: group } = storeToRefs(groupsStore)

onMounted(async () => {
  await Promise.all([
    recordsStore.fetchGroupDashboard(id),
    groupsStore.fetchGroup(id),
  ])
})
</script>
