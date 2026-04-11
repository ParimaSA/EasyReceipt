<template>
  <RouterLink
    :to="to"
    :class="[
      'flex items-center gap-3 rounded-xl transition-all duration-150',
      small ? 'px-3 py-1.5 text-xs' : 'px-3 py-2.5 text-sm',
      'hover:bg-gray-800 hover:text-white',
      'router-link-active:bg-amber-400/15 router-link-active:text-amber-300',
    ]"
  >
    <component :is="icon" :class="['flex-shrink-0', small ? 'w-3.5 h-3.5' : 'w-5 h-5']" />
    <span v-if="!collapsed" class="truncate font-medium">{{ label }}</span>
  </RouterLink>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Component } from 'vue'
defineProps<{
  to: object
  icon: Component
  label: string
  collapsed?: boolean
  small?: boolean
}>()
</script>
