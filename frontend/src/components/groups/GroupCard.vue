<template>
  <RouterLink
    :to="{ name: 'GroupDashboard', params: { id: group.id } }"
    class="card p-5 hover:shadow-lg transition-shadow group block"
  >
    <div class="flex items-start justify-between mb-3">
      <div class="w-10 h-10 rounded-xl bg-amber-400/20 flex items-center justify-center">
        <p v-if="group.icon">{{ group.icon }}</p>
        <UserGroupIcon v-else class="w-5 h-5 text-amber-600" />
      </div>
      <span :class="['badge', myRole === 'leader' ? 'badge-leader' : myRole === 'member' ? 'badge-member' : 'badge-viewer']">
        {{ myRole }}
      </span>
    </div>
    <h3 class="font-semibold truncate">{{ group.name }}</h3>
    <p v-if="group.description" class="text-xs mt-1 line-clamp-2">{{ group.description }}</p>
    <p class="text-xs mt-2">{{ group.members.length }} member{{ group.members.length !== 1 ? 's' : '' }}</p>
  </RouterLink>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { UserGroupIcon } from '@heroicons/vue/24/outline'
import type { Group } from '@/types'

const props = defineProps<{
  group: Group
  myRole: string
}>()
</script>