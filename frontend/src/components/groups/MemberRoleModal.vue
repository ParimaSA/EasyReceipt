<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm" @click.self="$emit('close')">
      <div class="bg-white rounded-2xl w-full max-w-sm shadow-2xl overflow-hidden">
        <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 class="text-lg font-semibold">Change Member Role</h2>
          <button @click="$emit('close')" class="p-2 rounded-lg hover:bg-gray-100">
            <XMarkIcon class="w-4 h-4" />
          </button>
        </div>

        <div v-if="targetMember" class="p-6 space-y-6">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 rounded-full bg-amber-100 flex items-center justify-center">
               <span class="text-amber-700 text-lg font-bold">
                  {{ targetMember.user?.username?.charAt(0).toUpperCase() }}
                </span>
            </div>
            <div>
              <p class="font-bold text-gray-900">{{ targetMember.user?.username }}</p>
              <p class="text-xs text-gray-500">Current Role: {{ targetMember.role }}</p>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Select New Role</label>
            <select
              v-model="newRole"
              class="input w-full"
            >
              <option value="member">Member</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          <div class="flex gap-3 pt-2">
            <button @click="$emit('close')" class="btn-ghost flex-1">Cancel</button>
            <button 
              @click="saveRole" 
              :disabled="loading" 
              class="btn-primary flex-1"
            >
              {{ loading ? 'Updating...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useGroupsStore } from '@/stores/groups'
import type { Group, GroupMemberRole } from '@/types'

const props = defineProps<{ 
  group: Group, 
  targetUserId: string 
}>()

const emit = defineEmits<{ close: [] }>()

const groupsStore = useGroupsStore()
const loading = ref(false)

// Find the specific member from the group
const targetMember = computed(() => 
  props.group.members.find(m => m.user_id === props.targetUserId)
)
const newRole = ref<GroupMemberRole>(targetMember.value?.role || 'member')

async function saveRole() {
  loading.value = true
  try {
    await groupsStore.updateMemberRole(props.group.id, props.targetUserId, newRole.value)
    emit('close')
  } finally {
    loading.value = false
  }
}
</script>