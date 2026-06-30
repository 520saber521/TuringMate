import axios from 'axios'

/**
 * 统一API响应格式
 * {
 *   success: boolean,
 *   data: any,
 *   message: string,
 *   meta: { request_id, page, page_size, total, has_more }
 * }
 */
interface APIResponse<T = any> {
  success: boolean
  data: T
  message: string
  meta?: {
    request_id?: string
    page?: number
    page_size?: number
    total?: number
    has_more?: boolean
  }
}

interface APIErrorResponse {
  success: false
  error: {
    code: string
    message: string
    details?: Record<string, any>
  }
  meta?: { request_id?: string }
}

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - attach auth token and request ID
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('turingmate_access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // Add request ID for tracing
    config.headers['X-Request-Id'] = `req_${Date.now()}_${Math.random().toString(36).slice(2)}`
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor - unwrap unified response format
apiClient.interceptors.response.use(
  (response) => {
    // Unwrap unified response: extract data from { success, data, message, meta }
    const unified = response.data as APIResponse
    if (unified.success && unified.data !== undefined) {
      return unified.data
    }
    // If not unified format, return original
    return response.data
  },
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

    // Extract error from unified error response
    const errorData: APIErrorResponse = error.response?.data
    const errorMessage = errorData?.error?.message || error.message || '请求失败'
    console.error('[API Error]', error.response?.status, errorMessage, errorData?.error?.details)
    return Promise.reject(new Error(errorMessage))
  },
)

export default apiClient
