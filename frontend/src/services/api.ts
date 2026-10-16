import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('civicfix_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('civicfix_token')
      // Redirect to login in Phase 2
    }
    return Promise.reject(error)
  }
)

export default api

// ── Health API ─────────────────────────────────────────────────
export const healthApi = {
  check: () => api.get<{ status: string; service: string; version: string; environment: string }>('/health'),
  detailed: () => api.get('/health/detailed'),
}
