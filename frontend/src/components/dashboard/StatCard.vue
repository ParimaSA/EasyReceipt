<template>
  <div class="card p-5 flex items-start gap-4">
    <div :class="['w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0', iconBg]">
      <component :is="icon" class="w-5 h-5" :class="iconColor" />
    </div>
    <div class="min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wider">{{ label }}</p>
      <p class="text-md sm:text-xl md:text-2xl font-mono font-semibold mt-0.5">
        {{ formattedValue }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

const props = defineProps<{
  label: string
  value: number
  icon: Component
  variant?: 'income' | 'expense' | 'neutral' | 'net'
  sub?: string
  currency?: string
}>()

const currency = props.currency ?? '฿'

const formattedValue = computed(() => {
  const abs = Math.abs(props.value)
  const formatted = abs.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  const prefix = props.value < 0 ? '-' : ''
  return `${prefix}${currency}${props.variant == 'neutral' ? abs : formatted}`
})

const iconBg = computed(() => ({
  income:  'bg-green-300',
  expense: 'bg-red-300',
  neutral: 'bg-blue-100',
  net:     props.value >= 0 ? 'bg-green-200' : 'bg-red-200',
}[props.variant ?? 'neutral']))

const iconColor = computed(() => ({
  income:  'text-green-600',
  expense: 'text-red-600',
  neutral: 'text-blue-500',
  net:     props.value >= 0 ? 'text-green-600' : 'text-red-600',
}[props.variant ?? 'neutral']))

</script>
