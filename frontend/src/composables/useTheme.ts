import { ref, computed, onMounted, onUnmounted } from 'vue'

export type ThemeMode = 'auto' | 'light' | 'dark'

const STORAGE_KEY = 'theme_preference'
const LIGHT_START = 6  // 6:00
const DARK_START = 18  // 18:00

function timeBasedTheme(): 'light' | 'dark' {
  const hour = new Date().getHours()
  return hour >= LIGHT_START && hour < DARK_START ? 'light' : 'dark'
}

const theme = ref<ThemeMode>('auto')
let checkInterval: ReturnType<typeof setInterval> | null = null

export function useTheme() {
  const resolvedTheme = computed<'light' | 'dark'>(() => {
    if (theme.value === 'auto') return timeBasedTheme()
    return theme.value
  })

  function applyTheme(t: 'light' | 'dark') {
    document.documentElement.setAttribute('data-theme', t)
  }

  function setTheme(mode: ThemeMode) {
    theme.value = mode
    localStorage.setItem(STORAGE_KEY, mode)
    applyTheme(resolvedTheme.value)
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY) as ThemeMode | null
    if (saved === 'light' || saved === 'dark' || saved === 'auto') {
      theme.value = saved
    }
    applyTheme(resolvedTheme.value)

    checkInterval = setInterval(() => {
      if (theme.value === 'auto') {
        applyTheme(timeBasedTheme())
      }
    }, 60_000)
  }

  onMounted(initTheme)

  onUnmounted(() => {
    if (checkInterval) {
      clearInterval(checkInterval)
      checkInterval = null
    }
  })

  return { theme, resolvedTheme, setTheme, initTheme }
}
