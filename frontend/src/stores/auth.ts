import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, register as apiRegister, refreshToken, getMe } from '@/api/auth'
import type { LoginParams, RegisterParams, UserInfo } from '@/api/auth'

const TOKEN_KEY = 'turingmate_access_token'
const REFRESH_KEY = 'turingmate_refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const refreshTokenValue = ref<string>(localStorage.getItem(REFRESH_KEY) || '')
  const isAuthenticated = computed(() => !!accessToken.value)

  function saveTokens(access: string, refresh: string) {
    accessToken.value = access
    refreshTokenValue.value = refresh
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_KEY, refresh)
  }

  function clearTokens() {
    accessToken.value = ''
    refreshTokenValue.value = ''
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_KEY)
  }

  async function login(params: LoginParams) {
    const res = await apiLogin(params)
    saveTokens(res.access_token, res.refresh_token)
    user.value = res.user
    return res
  }

  async function register(params: RegisterParams) {
    const res = await apiRegister(params)
    saveTokens(res.access_token, res.refresh_token)
    user.value = res.user
    return res
  }

  async function logout() {
    user.value = null
    clearTokens()
  }

  async function fetchUser() {
    if (!accessToken.value) return
    try {
      user.value = await getMe()
    } catch {
      // Try refresh
      if (refreshTokenValue.value) {
        try {
          const res = await refreshToken(refreshTokenValue.value)
          saveTokens(res.access_token, res.refresh_token)
          user.value = res.user
        } catch {
          clearTokens()
        }
      } else {
        clearTokens()
      }
    }
  }

  async function tryRestoreSession() {
    if (accessToken.value && !user.value) {
      await fetchUser()
    }
  }

  return {
    user,
    accessToken,
    refreshTokenValue,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    tryRestoreSession,
  }
})
