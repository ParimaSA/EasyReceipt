import { defineStore } from 'pinia'
import { ref } from 'vue'
import { groupsApi } from '@/api'
import type { Group, Invitation, GroupMemberRole } from '@/types'

export const useGroupsStore = defineStore('groups', () => {
  const groups = ref<Group[]>([])
  const currentGroup = ref<Group | null>(null)
  const invitations = ref<Invitation[]>([])
  const loading = ref(false)

  async function mockGroups() {
    groups.value = []
  }

  async function fetchGroups() {
    loading.value = true
    try {
      const { data } = await groupsApi.list()
      groups.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchGroup(id: string) {
    const { data } = await groupsApi.get(id)
    currentGroup.value = data
    return data
  }

  async function createGroup(payload: { name: string; description?: string }) {
    const { data } = await groupsApi.create(payload)
    groups.value.push(data)
    return data
  }

  async function updateGroup(id: string, payload: { name?: string; description?: string }) {
    const { data } = await groupsApi.update(id, payload)
    const idx = groups.value.findIndex(g => g.id === id)
    if (idx !== -1) groups.value[idx] = data
    if (currentGroup.value?.id === id) currentGroup.value = data
    return data
  }

  async function deleteGroup(id: string) {
    await groupsApi.delete(id)
    groups.value = groups.value.filter(g => g.id !== id)
    if (currentGroup.value?.id === id) currentGroup.value = null
  }

  async function fetchInvitations(groupId: string) {
    const { data } = await groupsApi.listInvitations(groupId)
    invitations.value = data
  }

  async function createInvitation(groupId: string, payload: {
    invited_role: GroupMemberRole; max_uses?: number; expires_hours?: number
  }) {
    const { data } = await groupsApi.createInvitation(groupId, payload)
    invitations.value.push(data)
    return data
  }

  async function revokeInvitation(groupId: string, invitationId: string) {
    await groupsApi.revokeInvitation(groupId, invitationId)
    invitations.value = invitations.value.filter(i => i.id !== invitationId)
  }

  async function joinGroup(token: string) {
    const { data } = await groupsApi.join(token)
    if (!groups.value.find(g => g.id === data.id)) groups.value.push(data)
    return data
  }

  async function removeMember(groupId: string, userId: string) {
    await groupsApi.removeMember(groupId, userId)
    if (currentGroup.value?.id === groupId) {
      currentGroup.value.members = currentGroup.value.members.filter(m => m.user_id !== userId)
    }
  }

  return {
    groups, currentGroup, invitations, loading,
    mockGroups, fetchGroups, fetchGroup, createGroup, updateGroup, deleteGroup,
    fetchInvitations, createInvitation, revokeInvitation, joinGroup, removeMember,
  }
})
