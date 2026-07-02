import axios, { type AxiosRequestConfig } from 'axios'

type ApiClient = {
  get<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
  post<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  put<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  patch<T = unknown>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T>
  delete<T = unknown>(url: string, config?: AxiosRequestConfig): Promise<T>
}

function getErrorMessage(error: any): string {
  const detail = error.response?.data?.detail || error.response?.data?.message
  if (typeof detail === 'string' && detail.trim()) return detail

  if (error.code === 'ECONNABORTED') return '请求超时，请稍后重试'
  if (!error.response) return '无法连接到服务器，请确认后端服务是否已启动'

  const statusMessages: Record<number, string> = {
    400: '请求参数有误，请检查后重试',
    401: '登录已过期，请重新登录',
    403: '当前账号没有权限执行此操作',
    404: '没有找到对应数据',
    500: '服务器暂时不可用，请稍后重试',
  }

  return statusMessages[error.response.status] || '请求失败，请稍后重试'
}

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

    error.userMessage = getErrorMessage(error)
    console.error('[API Error]', error.response?.status, error.response?.data)
    return Promise.reject(error)
  },
)

export default apiClient as ApiClient
