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
    groups.value = [
      {
        id: 'g-1',
        name: 'Family',
        description: 'Family shared expenses',
        leader_id: 'user-1',
        is_active: true,
        created_at: '2024-01-01T00:00:00',
        members: [
          {
            id: 'gm-1', user_id: 'user-1', group_id: 'g-1', role: 'leader',
            joined_at: '2024-01-01T00:00:00',
            user: { id: 'user-1', username: 'prima' },
          },
          {
            id: 'gm-2', user_id: 'user-2', group_id: 'g-1', role: 'member',
            joined_at: '2024-01-02T00:00:00',
            user: { id: 'user-2', username: 'mom' },
          },
          {
            id: 'gm-3', user_id: 'user-3', group_id: 'g-1', role: 'viewer',
            joined_at: '2024-01-03T00:00:00',
            user: { id: 'user-3', username: 'dad' },
          },
        ],
      },
      {
        id: 'g-2',
        name: 'Work Team',
        description: 'Office and work related expenses',
        leader_id: 'user-1',
        is_active: true,
        created_at: '2024-02-01T00:00:00',
        members: [
          {
            id: 'gm-4', user_id: 'user-1', group_id: 'g-2', role: 'leader',
            joined_at: '2024-02-01T00:00:00',
            user: { id: 'user-1', username: 'prima' },
          },
          {
            id: 'gm-5', user_id: 'user-4', group_id: 'g-2', role: 'member',
            joined_at: '2024-02-02T00:00:00',
            user: { id: 'user-4', username: 'alice' },
          },
        ],
      },
      {
        id: 'g-3',
        name: 'Trip 2024',
        icon: '⛱',
        description: 'Expenses for our 2024 trip',
        leader_id: 'user-2',
        is_active: true,
        created_at: '2024-03-01T00:00:00',
        members: [
          {
            id: 'gm-6', user_id: 'user-2', group_id: 'g-3', role: 'leader',
            joined_at: '2024-03-01T00:00:00',
            user: { id: 'user-2', username: 'mom' },
          },
          {
            id: 'gm-7', user_id: 'user-1', group_id: 'g-3', role: 'member',
            joined_at: '2024-03-02T00:00:00',
            user: { id: 'user-1', username: 'prima' },
          },
          {
            id: 'gm-8', user_id: 'user-5', group_id: 'g-3', role: 'viewer',
            joined_at: '2024-03-03T00:00:00',
            user: { id: 'user-5', username: 'bob' },
          },
        ],
      },
    ] as Group[]
  }

  function mockGroup(id: string) {
    mockGroups()
    currentGroup.value = groups.value.find(g => g.id == id) ?? null
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
    mockGroups, mockGroup, fetchGroups, fetchGroup, createGroup, updateGroup, deleteGroup,
    fetchInvitations, createInvitation, revokeInvitation, joinGroup, removeMember,
  }
})
