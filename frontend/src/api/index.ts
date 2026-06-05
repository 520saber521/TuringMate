import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - attach auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('turingmate_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response.data,
  async (error) => {
    const originalRequest = error.config

    // 401 - try token refresh once
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshTokenValue = localStorage.getItem('turingmate_refresh_token')
      if (refreshTokenValue) {
        try {
          const res = await apiClient.post('/auth/refresh', { refresh_token: refreshTokenValue }) as any
          const { access_token, refresh_token } = res
          localStorage.setItem('turingmate_access_token', access_token)
          localStorage.setItem('turingmate_refresh_token', refresh_token)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch {
          // Refresh failed - clear tokens and redirect to login
          localStorage.removeItem('turingmate_access_token')
          localStorage.removeItem('turingmate_refresh_token')
          window.location.href = '/login'
        }
      }
    }

    console.error('[API Error]', error.response?.status, error.response?.data)
    return Promise.reject(error)
  },
)

export default apiClient
