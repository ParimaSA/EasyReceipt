<template>
  <div class="p-12 space-y-6 max-w-6xl mx-auto">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold">{{ group?.name }}</h1>
        <p v-if="group?.description" class="text-sm text-gray-400 mt-0.5">{{ group.description }}</p>
      </div>
      <div class="flex gap-2">
        <RouterLink :to="{ name: 'GroupDashboard', params: { id } }" class="btn-ghost text-sm">Dashboard</RouterLink>
        <RouterLink :to="{ name: 'GroupRecords', params: { id } }" class="btn-ghost text-sm">Records</RouterLink>
      </div>
    </div>

    <MemberList
      :members="group?.members ?? []"
      :is-leader="isLeader"
      :current-user-id="authStore.user?.id"
      @invite="showInvite = true"
      @remove="removeMember"
    />

    <InviteList
      v-if="isLeader"
      :invitations="invitations"
      @copy="copyLink"
      @revoke="revokeInvitation"
    />

    <InviteModal
      v-if="showInvite"
      :loading="creatingInvite"
      @close="showInvite = false"
      @submit="createInvite"
    />

    <!-- Modals -->
    <ConfirmDialog
      v-if="deletingMember"
      title="Remove Member"
      :message="`Remove &quot;${deletingMemberName}&quot; from the group? They will lose access.`"
      @confirm="doRemove"
      @cancel="deletingMember = null"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import type { Invitation } from '@/types'
import MemberList from '@/components/groups/MemberList.vue'
import InviteList from '@/components/groups/InviteList.vue'
import InviteModal from '@/components/groups/InviteModal.vue'
import ConfirmDialog from '@/components/common/ConfirmDialog.vue'

const route = useRoute()
const id = route.params.id as string
const groupsStore = useGroupsStore()
const authStore = useAuthStore()
const { currentGroup: group, invitations } = storeToRefs(groupsStore)

const isLeader = computed(() =>
  group.value?.members.find(m => m.user_id === authStore.user?.id)?.role === 'leader'
)

const showInvite = ref(false)
const creatingInvite = ref(false)

const deletingMember = ref<string | null>(null)
const deletingMemberName = computed(() =>
  group.value?.members.find(m => m.user_id === deletingMember.value)?.user?.username
)

onMounted(async () => {
  if (isLeader.value) await groupsStore.fetchInvitations(id)
})

async function createInvite(form: any) {
  creatingInvite.value = true
  try {
    await groupsStore.createInvitation(id, form)
    showInvite.value = false
  } finally { creatingInvite.value = false }
}

async function revokeInvitation(invId: string) {
  await groupsStore.revokeInvitation(id, invId)
}

async function removeMember(userId: string) {
  deletingMember.value = userId
}

async function doRemove() {
  if (!deletingMember.value) return
  await groupsStore.removeMember(id, deletingMember.value)
  deletingMember.value = null
}

function copyLink(inv: Invitation) {
  const url = inv.invite_url || `${window.location.origin}/join/${inv.token}`
  navigator.clipboard.writeText(url)
}
</script>