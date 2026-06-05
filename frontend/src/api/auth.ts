import apiClient from './index'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  password: string
  name: string
  email?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: {
    id: string
    username: string
    name: string
    avatar: string
    email: string
    target_school: string
    weak_subjects: string[]
  }
}

export interface UserInfo {
  id: string
  username: string
  name: string
  avatar: string
  email: string
  target_school: string
  weak_subjects: string[]
}

export function login(params: LoginParams): Promise<AuthResponse> {
  return apiClient.post('/auth/login', params) as any
}

export function register(params: RegisterParams): Promise<AuthResponse> {
  return apiClient.post('/auth/register', params) as any
}

export function refreshToken(token: string): Promise<AuthResponse> {
  return apiClient.post('/auth/refresh', { refresh_token: token }) as any
}

export function getMe(): Promise<UserInfo> {
  return apiClient.get('/auth/me') as any
}
