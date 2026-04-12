import axios from 'axios'
import type { Token } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})


// Attach access_token to request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let refreshing = false
let failedQueue: Array<{ resolve: (v: any) => void; reject: (e: any) => void }> = []

function processQueue(error: any, token: string | null = null) {
  failedQueue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve(token)))
  failedQueue = []
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      if (refreshing) {
        return new Promise((resolve, reject) => failedQueue.push({ resolve, reject }))
          .then((token) => { original.headers.Authorization = `Bearer ${token}`; return api(original) })
          .catch((e) => Promise.reject(e))
      }
      original._retry = true
      refreshing = true
      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) throw new Error('No refresh token')
        const { data } = await axios.post<Token>('/api/v1/auth/refresh', { refresh_token: refresh })
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        api.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
        processQueue(null, data.access_token)
        return api(original)
      } catch (e) {
        processQueue(e, null)
        localStorage.clear()
        window.location.href = '/login'
        return Promise.reject(e)
      } finally {
        refreshing = false
      }
    }
    return Promise.reject(error)
  }
)

export default api
