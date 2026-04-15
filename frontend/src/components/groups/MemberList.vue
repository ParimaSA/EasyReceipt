<template>
  <div class="card p-5">
    <div class="flex items-center justify-between mb-4">
      <h2 class="font-semibold">Members</h2>
      <button v-if="isLeader" @click="$emit('invite')" class="btn-primary text-xs py-2 px-3">
        <LinkIcon class="w-3.5 h-3.5" /> Invite
      </button>
    </div>
    <div class="space-y-2">
      <div
        v-for="m in members" :key="m.id"
        class="flex items-center gap-3 py-2 px-3 rounded-xl hover:bg-slate-50 group"
      >
        <div :class="[
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          m.role === 'leader' ? 'bg-green-200 text-green-800' :
          m.role === 'member' ? 'bg-blue-200 text-blue-800' :
          'bg-gray-200 text-gray-500'
        ]">
          <span class="text-xs font-bold">{{ m.user?.username?.[0]?.toUpperCase() }}</span>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-800">{{ m.user?.username }}</p>
        </div>
        <span :class="['badge', m.role === 'leader' ? 'badge-leader' : m.role === 'member' ? 'badge-member' : 'badge-viewer']">
          {{ m.role }}
        </span>

        <!-- Actions (if Leader) -->
        <div v-if="isLeader && m.user_id !== currentUserId" class="flex items-center gap-1 text-gray-500">
          <button @click="$emit('edit', m.user_id)" class="p-1.5 rounded-lg hover:bg-blue-100">
            <PencilSquareIcon class="w-3.5 h-3.5" />
          </button>
          <button @click="$emit('remove', m.user_id)" class="p-1.5 rounded-lg hover:bg-gray-200">
            <TrashIcon class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { TrashIcon, LinkIcon, PencilSquareIcon } from '@heroicons/vue/24/outline'
import type { GroupMember } from '@/types'

defineProps<{
  members: GroupMember[]
  isLeader: boolean
  currentUserId?: string
}>()

defineEmits<{
  invite: []
  remove: [userId: string]
  edit: [userId: string]
}>()
</script>