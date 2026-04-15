import api from './client'
import type {
  Token, User, Record, Paginated, Dashboard,
  Group, Invitation, Category, RecordType, GroupMemberRole,
} from '@/types'

export const authApi = {
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post<Token>('/auth/register', data),
  login: (email: string, password: string) =>
    api.post<Token>('/auth/login', { email, password }),
  me: () => api.get<User>('/auth/me'),
}

export const recordsApi = {
  listPersonal: (params?: {
    skip?: number; limit?: number; type?: RecordType
    category_id?: string; date_from?: string; date_to?: string
  }) => api.get<Paginated<Record>>('/records/personal', { params }),

  listGroup: (groupId: string, params?: {
    skip?: number; limit?: number; type?: RecordType
    date_from?: string; date_to?: string
  }) => api.get<Paginated<Record>>(`/records/group/${groupId}`, { params }),

  personalDashboard: (params?: { date_from?: string; date_to?: string }) =>
    api.get<Dashboard>('/records/personal/dashboard', { params }),

  groupDashboard: (groupId: string, params?: { date_from?: string; date_to?: string }) =>
    api.get<Dashboard>(`/records/group/${groupId}/dashboard`, { params }),

  create: (data: {
    title: string; amount: number; type: RecordType; date: string
    note?: string; category_id?: string; group_id?: string
  }) => api.post<Record>('/records', data),

  update: (id: string, data: Partial<{
    title: string; amount: number; type: RecordType
    note: string; date: string; category_id: string
  }>) => api.put<Record>(`/records/${id}`, data),

  delete: (id: string) => api.delete(`/records/${id}`),

  scan: (file: File) => {
    const fd = new FormData(); fd.append('file', file)
    return api.post<{ title?: string; amount?: number; date?: string; raw_text: string }>('/records/scan', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const groupsApi = {
  list: () => api.get<Group[]>('/groups'),
  get: (id: string) => api.get<Group>(`/groups/${id}`),
  create: (data: { name: string; description?: string }) => api.post<Group>('/groups/', data),
  update: (id: string, data: { name?: string; description?: string }) =>
    api.put<Group>(`/groups/${id}`, data),
  delete: (id: string) => api.delete(`/groups/${id}`),

  // Invitations
  createInvitation: (groupId: string, data: {
    invited_role: GroupMemberRole; max_uses?: number; expires_hours?: number
  }) => api.post<Invitation>(`/groups/${groupId}/invitations`, data),
  listInvitations: (groupId: string) =>
    api.get<Invitation[]>(`/groups/${groupId}/invitations`),
  revokeInvitation: (groupId: string, invitationId: string) =>
    api.delete(`/groups/${groupId}/invitations/${invitationId}`),
  join: (token: string) => api.post<Group>('/groups/join', { token }),

  // Members
  removeMember: (groupId: string, userId: string) =>
    api.delete(`/groups/${groupId}/members/${userId}`),
  updateMemberRole: (groupId: string, userId: string, new_role: GroupMemberRole) =>
    api.patch(`/groups/${groupId}/members/${userId}/role`, null, { params: { new_role } }),
}


export const categoriesApi = {
  list: () => api.get<Category[]>('/categories'),
  create: (data: { name: string; icon?: string; color?: string }) =>
    api.post<Category>('/categories', data),
  delete: (id: string) => api.delete(`/categories/${id}`),
}