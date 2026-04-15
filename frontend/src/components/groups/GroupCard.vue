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

    <!-- Actions (only for Leader) -->
    <div v-if="myRole === 'leader'" class="w-full flex justify-end items-center gap-1 text-gray-500" ref="menuRef">
      <button @click.stop.prevent="onEdit" class="p-1.5 rounded-lg hover:bg-blue-100">
        <PencilSquareIcon class="w-3.5 h-3.5" />
      </button>
      <button @click.stop.prevent="onDelete" class="p-1.5 rounded-lg hover:bg-gray-200">
        <TrashIcon class="w-3.5 h-3.5" />
      </button>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { UserGroupIcon, PencilSquareIcon, TrashIcon } from '@heroicons/vue/24/outline'

import type { Group } from '@/types'

const props = defineProps<{
  group: Group
  myRole: string
}>()

console.log("role: ", props.myRole)

const emit = defineEmits<{
  edit: [group: Group]
  delete: [group: Group]
}>()

const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

function onEdit() {
  menuOpen.value = false
  emit('edit', props.group)
}

function onDelete() {
  menuOpen.value = false
  emit('delete', props.group)
}

function handleOutsideClick(e: MouseEvent) {
  if (menuRef.value && !menuRef.value.contains(e.target as Node)) {
    menuOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleOutsideClick))
onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>