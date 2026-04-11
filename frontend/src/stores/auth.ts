import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isLeader = computed(() => user.value?.role === 'leader')
  const isViewer = computed(() => user.value?.role === 'viewer')

  async function fetchMe() {
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      user.value = null
    }
  }

  async function login(email: string, password: string) {
    loading.value = true
    try {
      const { data } = await authApi.login(email, password)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  async function register(payload: {
    email: string; username: string; password: string; full_name?: string
  }) {
    loading.value = true
    try {
      const { data } = await authApi.register(payload)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
    } finally {
      loading.value = false
    }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
  }

  return { user, loading, isAuthenticated, isLeader, isViewer, fetchMe, login, register, logout }
})
