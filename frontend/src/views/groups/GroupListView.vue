<template>
  <div class="p-12 space-y-5 max-w-6xl mx-auto">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold">Groups</h1>
      <button @click="showCreate = true" class="btn-primary">
        <PlusIcon class="w-4 h-4" /> New Group
      </button>
    </div>

    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-for="i in 3" :key="i" class="card p-5 h-32 animate-pulse bg-gray-100" />
    </div>

    <div v-else-if="groups.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <GroupCard
        v-for="g in groups" :key="g.id"
        :group="g"
        :my-role="myRole(g)"
        @edit="onEditGroup"
        @delete="onDeleteGroup"
      />
    </div>

    <div v-else class="card p-12 text-center">
      <UserGroupIcon class="w-12 h-12 text-gray-300 mx-auto mb-3" />
      <p class="text-gray-500 text-sm">No groups yet. Create one or join via an invite link.</p>
    </div>
  </div>

  <CreateGroupModal
    v-if="showCreate"
    @close="showCreate = false"
    @created="onCreated"
  />

  <EditGroupModal
    v-if="editingGroup"
    :group="editingGroup"
    @close="editingGroup = null"
    @updated="onUpdated"
  />

  <ConfirmDialog
    v-if="deletingGroup"
    title="Delete Group"
    :message="`Delete group &quot;${deletingGroup.name}&quot;? This cannot be undone.`"
    @confirm="confirmDelete"
    @cancel="deletingGroup = null"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PlusIcon, UserGroupIcon } from '@heroicons/vue/24/outline'
import { useGroupsStore } from '@/stores/groups'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import type { Group } from '@/types'
import GroupCard from '@/components/groups/GroupCard.vue'
import CreateGroupModal from '@/components/groups/CreateGroupModal.vue'
import EditGroupModal from '@/components/groups/EditGroupModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const groupsStore = useGroupsStore()
const authStore = useAuthStore()
const { groups, loading } = storeToRefs(groupsStore)

const showCreate = ref(false)
const editingGroup = ref<Group | null>(null)
const deletingGroup = ref<Group | null>(null)
const deleteLoading = ref(false)

function myRole(g: Group) {
  return g.members.find(m => m.user_id === authStore.user?.id)?.role ?? 'viewer'
}

async function onCreated(payload: { name: string; icon: string; description: string }) {
  await groupsStore.createGroup(payload)
  showCreate.value = false
}

function onEditGroup(group: Group) {
  editingGroup.value = group
}

async function onUpdated(payload: { id: string; name: string; icon: string; description: string }) {
  await groupsStore.updateGroup(editingGroup.value!.id, payload)
  editingGroup.value = null
}

function onDeleteGroup(group: Group) {
  deletingGroup.value = group
}

async function confirmDelete() {
  if (!deletingGroup.value) return
  deleteLoading.value = true
  try {
    await groupsStore.deleteGroup(deletingGroup.value.id)
    deletingGroup.value = null
  } finally {
    deleteLoading.value = false
  }
}

onMounted(() => groupsStore.fetchGroups())
</script>