<template>
  <div class="flex items-center gap-3 py-2.5 px-3 rounded-xl transition-colors group">
    <!-- Type (income/expense) -->
    <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
      record.type === 'income' ? 'bg-green-200' : 'bg-red-200']">
      <component
        :is="record.type === 'income' ? ArrowDownLeftIcon : ArrowUpRightIcon"
        :class="['w-4 h-4', record.type === 'income' ? 'text-green-600' : 'text-red-600']"
      />
    </div>

    <!-- Info -->
    <div class="flex-1 min-w-0">
      <p class="font-medium truncate">{{ record.title }}</p>
      <p class="text-xs">
        {{ formatDate(record.date) }}
        <span v-if="record.category" class="ml-1">· {{ record.category.icon }} {{ record.category.name }}</span>
      </p>
    </div>

    <!-- Amount -->
    <p :class="['font-mono text-sm font-semibold flex-shrink-0',
      record.type === 'income' ? 'text-green-600' : 'text-red-600']">
      {{ record.type === 'income' ? '+' : '-' }}฿{{ record.amount.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
    </p>

    <!-- Actions (if not readOnly) -->
    <div v-if="!readOnly" class="flex items-center gap-1 text-gray-500">
      <button @click="$emit('edit', record)" class="p-1.5 rounded-lg hover:bg-blue-100">
        <PencilSquareIcon class="w-3.5 h-3.5" />
      </button>
      <button @click="$emit('delete', record)" class="p-1.5 rounded-lg hover:bg-gray-200">
        <TrashIcon class="w-3.5 h-3.5" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ArrowDownLeftIcon, ArrowUpRightIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import type { Record } from '@/types'

defineProps<{ record: Record; readOnly?: boolean }>()
defineEmits<{ edit: [record: Record]; delete: [record: Record] }>()

function formatDate(d: string) {
  return format(new Date(d), 'MMM d, yyyy')
}
</script>
