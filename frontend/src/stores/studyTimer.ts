import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const DEFAULT_GOAL_MINUTES = 64
const TICK_INTERVAL = 15 // seconds — tick every 15s
const IDLE_TIMEOUT = 5 * 60 * 1000 // 5 min no interaction = idle

// Pomodoro defaults (seconds)
const FOCUS_DURATION = 25 * 60
const SHORT_BREAK_DURATION = 5 * 60
const LONG_BREAK_DURATION = 15 * 60
const SESSIONS_BEFORE_LONG_BREAK = 4

const STUDY_ROUTES: Record<string, string> = {
  '/chat': '数据结构',
  '/photo-search': '题目识别',
  '/correction': '手写批改',
  '/visualize': '代码实战',
  '/code-challenge': '代码挑战',
  '/problem-gen': '举一反三',
  '/learning-path': '学习规划',
  '/diagnosis': '薄弱诊断',
}

// ── Achievements ──
interface Achievement {
  id: string
  title: string
  desc: string
  icon: string
  condition: () => boolean
}

function dateKey(offset = 0): string {
  const d = new Date()
  d.setDate(d.getDate() - offset)
  return `study_${d.getFullYear()}_${d.getMonth() + 1}_${d.getDate()}`
}

function weekDayLabel(offset: number): string {
  const labels = ['日', '一', '二', '三', '四', '五', '六']
  const d = new Date()
  d.setDate(d.getDate() - offset)
  return labels[d.getDay()]
}

export interface DaySnapshot {
  label: string
  minutes: number
  isToday: boolean
  reached: boolean
}

export interface SubjectSlice {
  subject: string
  minutes: number
  color: string
}

export type PomodoroPhase = 'idle' | 'focus' | 'short_break' | 'long_break'

const SUBJECT_COLORS: Record<string, string> = {
  '数据结构': '#7c3aed',
  '题目识别': '#0ea5e9',
  '手写批改': '#059669',
  '代码实战': '#e11d48',
  '代码挑战': '#e11d48',
  '举一反三': '#a78bfa',
  '学习规划': '#059669',
  '薄弱诊断': '#f59e0b',
}

function notify(title: string, body: string) {
  if (!('Notification' in window)) return
  if (Notification.permission === 'granted') {
    new Notification(title, { body, icon: '/favicon.ico' })
  }
}

export const useStudyTimerStore = defineStore('studyTimer', () => {
  // ── Core state ──
  const todaySeconds = ref(0)
  const isActive = ref(false)
  const streakDays = ref(0)
  const lastActiveDate = ref(dateKey())
  const goalMinutes = ref(DEFAULT_GOAL_MINUTES)
  const currentRoute = ref('')

  // ── Pomodoro state ──
  const pomodoroPhase = ref<PomodoroPhase>('idle')
  const pomodoroRemaining = ref(FOCUS_DURATION)
  const pomodoroRunning = ref(false)
  const focusCount = ref(0)

  // ── Subject tracking ──
  const subjectTimes = ref<Record<string, number>>({})

  // ── Achievements ──
  const unlockedAchievements = ref<string[]>([])

  let tickHandle: ReturnType<typeof setInterval> | null = null
  let pomodoroHandle: ReturnType<typeof setInterval> | null = null
  let lastInteraction = Date.now()

  // ── Computed ──
  const todayMinutes = computed(() => Math.round(todaySeconds.value / 60))
  const progressPercent = computed(() => Math.min(Math.round((todayMinutes.value / goalMinutes.value) * 100), 100))
  const isGoalReached = computed(() => todayMinutes.value >= goalMinutes.value)

  const pomodoroMinutes = computed(() => Math.ceil(pomodoroRemaining.value / 60))
  const pomodoroSeconds = computed(() => pomodoroRemaining.value % 60)
  const pomodoroDisplay = computed(() => {
    const m = pomodoroMinutes.value
    const s = pomodoroSeconds.value
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })

  const phaseLabel = computed(() => {
    const map: Record<string, string> = {
      idle: '准备就绪',
      focus: '专注中',
      short_break: '短休息',
      long_break: '长休息',
    }
    return map[pomodoroPhase.value]
  })

  const phaseEmoji = computed(() => {
    const map: Record<string, string> = {
      idle: '☕',
      focus: '🎯',
      short_break: '🌿',
      long_break: '😴',
    }
    return map[pomodoroPhase.value]
  })

  const focusCountToday = computed(() => focusCount.value)

  /** Last 7 days for mini chart */
  const weeklyData = computed<DaySnapshot[]>(() => {
    const days: DaySnapshot[] = []
    for (let i = 6; i >= 0; i--) {
      const key = dateKey(i)
      const raw = localStorage.getItem(key)
      const mins = raw ? Math.round(Number(raw) / 60) : 0
      days.push({
        label: weekDayLabel(i),
        minutes: mins,
        isToday: i === 0,
        reached: mins >= goalMinutes.value,
      })
    }
    return days
  })

  const weeklyTotal = computed(() => weeklyData.value.reduce((s, d) => s + d.minutes, 0))
  const weeklyAvg = computed(() => Math.round(weeklyTotal.value / 7))

  /** Subject breakdown for today */
  const subjectBreakdown = computed<SubjectSlice[]>(() => {
    const entries = Object.entries(subjectTimes.value)
    if (!entries.length) return []
    const total = entries.reduce((s, [, v]) => s + v, 0)
    return entries
      .map(([subject, seconds]) => ({
        subject,
        minutes: Math.round(seconds / 60),
        color: SUBJECT_COLORS[subject] || '#7c3aed',
        percent: total > 0 ? Math.round((seconds / total) * 100) : 0,
      }))
      .sort((a, b) => b.minutes - a.minutes)
  })

  // ── Achievements definition ──
  const achievementDefs: Achievement[] = [
    {
      id: 'first_goal',
      title: '初露锋芒',
      desc: '第一次达成每日目标',
      icon: '🎯',
      condition: () => todayMinutes.value >= goalMinutes.value,
    },
    {
      id: 'streak_7',
      title: '七日之约',
      desc: '连续学习 7 天',
      icon: '🔥',
      condition: () => streakDays.value >= 7,
    },
    {
      id: 'streak_30',
      title: '月度之星',
      desc: '连续学习 30 天',
      icon: '⭐',
      condition: () => streakDays.value >= 30,
    },
    {
      id: 'hour_2',
      title: '学海无涯',
      desc: '单日学习超过 2 小时',
      icon: '📚',
      condition: () => todayMinutes.value >= 120,
    },
    {
      id: 'hour_100',
      title: '百时里程碑',
      desc: '累计学习 100 小时',
      icon: '🏅',
      condition: () => {
        let total = 0
        for (let i = 0; i < 365; i++) {
          const raw = localStorage.getItem(dateKey(i))
          total += raw ? Number(raw) : 0
        }
        return total >= 100 * 3600
      },
    },
    {
      id: 'pomodoro_4',
      title: '番茄达人',
      desc: '一天完成 4 个番茄钟',
      icon: '🍅',
      condition: () => focusCount.value >= 4,
    },
    {
      id: 'all_subjects',
      title: '全科覆盖',
      desc: '一天学习 4 个不同科目',
      icon: '🌈',
      condition: () => Object.keys(subjectTimes.value).length >= 4,
    },
    {
      id: 'early_bird',
      title: '早鸟计划',
      desc: '早上 8 点前开始学习',
      icon: '🌅',
      condition: () => new Date().getHours() < 8 && todayMinutes.value >= 30,
    },
  ]

  function checkAchievements() {
    for (const def of achievementDefs) {
      if (unlockedAchievements.value.includes(def.id)) continue
      try {
        if (def.condition()) {
          unlockedAchievements.value.push(def.id)
          localStorage.setItem('study_achievements', JSON.stringify(unlockedAchievements.value))
        }
      } catch { /* condition may fail during init */ }
    }
  }

  function loadAchievements() {
    try {
      const raw = localStorage.getItem('study_achievements')
      if (raw) unlockedAchievements.value = JSON.parse(raw)
    } catch { /* ignore */ }
  }

  // ── Persistence ──
  function persist() {
    localStorage.setItem(dateKey(), String(todaySeconds.value))
  }

  function persistSubjects() {
    localStorage.setItem(`subjects_${dateKey()}`, JSON.stringify(subjectTimes.value))
  }

  function loadSubjects() {
    try {
      const raw = localStorage.getItem(`subjects_${dateKey()}`)
      if (raw) subjectTimes.value = JSON.parse(raw)
    } catch { /* ignore */ }
  }

  function setGoal(minutes: number) {
    if (minutes < 10 || minutes > 480) return
    goalMinutes.value = minutes
    localStorage.setItem('study_goal', String(minutes))
    recalcStreak()
  }

  function recalcStreak() {
    let streak = 0
    for (let i = 0; i < 365; i++) {
      const key = dateKey(i)
      const raw = localStorage.getItem(key)
      const mins = raw ? Math.round(Number(raw) / 60) : 0
      if (mins >= goalMinutes.value) {
        streak++
      } else if (i === 0) {
        continue
      } else {
        break
      }
    }
    streakDays.value = streak
  }

  function checkNewDay() {
    const today = dateKey()
    if (today !== lastActiveDate.value) {
      recalcStreak()
      lastActiveDate.value = today
      todaySeconds.value = Number(localStorage.getItem(today) || '0')
      subjectTimes.value = {}
      loadSubjects()
      focusCount.value = 0
      pomodoroPhase.value = 'idle'
      pomodoroRunning.value = false
    }
  }

  // ── Subject tracking ──
  function resolveSubject(path: string): string | null {
    for (const [prefix, subject] of Object.entries(STUDY_ROUTES)) {
      if (path.startsWith(prefix)) return subject
    }
    return null
  }

  function trackSubjectTick() {
    const subject = resolveSubject(currentRoute.value)
    if (!subject) return
    subjectTimes.value[subject] = (subjectTimes.value[subject] || 0) + TICK_INTERVAL
  }

  // ── Notifications ──
  function requestNotificationPermission() {
    if (!('Notification' in window)) return
    if (Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }

  // ── Pomodoro engine ──
  function startPomodoroTick() {
    if (pomodoroHandle) return
    pomodoroHandle = setInterval(() => {
      if (!pomodoroRunning.value) return

      pomodoroRemaining.value--

      if (pomodoroRemaining.value <= 0) {
        onPhaseComplete()
      }
    }, 1000)
  }

  function stopPomodoroTick() {
    if (pomodoroHandle) {
      clearInterval(pomodoroHandle)
      pomodoroHandle = null
    }
  }

  function onPhaseComplete() {
    if (pomodoroPhase.value === 'focus') {
      // Focus session done
      focusCount.value++
      notify('番茄钟完成', `已完成 ${focusCount.value} 个专注时段，休息一下吧`)
      checkAchievements()

      if (focusCount.value % SESSIONS_BEFORE_LONG_BREAK === 0) {
        pomodoroPhase.value = 'long_break'
        pomodoroRemaining.value = LONG_BREAK_DURATION
        notify('该休息了', `已完成 ${SESSIONS_BEFORE_LONG_BREAK} 个番茄钟，来个 ${LONG_BREAK_DURATION / 60} 分钟长休息`)
      } else {
        pomodoroPhase.value = 'short_break'
        pomodoroRemaining.value = SHORT_BREAK_DURATION
      }

      // Auto-pause tracking during break
      isActive.value = false
    } else {
      // Break done
      pomodoroPhase.value = 'idle'
      pomodoroRunning.value = false
      pomodoroRemaining.value = FOCUS_DURATION
      notify('休息结束', '准备好了吗？开始下一个番茄钟')
    }
  }

  function startFocus() {
    checkNewDay()
    requestNotificationPermission()
    lastInteraction = Date.now()

    if (pomodoroPhase.value === 'idle') {
      pomodoroPhase.value = 'focus'
      pomodoroRemaining.value = FOCUS_DURATION
    }

    pomodoroRunning.value = true
    isActive.value = true
    startTick()
    startPomodoroTick()
  }

  function pausePomodoro() {
    pomodoroRunning.value = false
    isActive.value = false
  }

  function resumePomodoro() {
    lastInteraction = Date.now()
    pomodoroRunning.value = true
    isActive.value = true
    startPomodoroTick()
  }

  function skipBreak() {
    pomodoroPhase.value = 'idle'
    pomodoroRunning.value = false
    pomodoroRemaining.value = FOCUS_DURATION
    startFocus()
  }

  // ── Tick engine (accumulates study time) ──
  function startTick() {
    if (tickHandle) return
    tickHandle = setInterval(() => {
      if (!isActive.value) return

      const now = Date.now()
      if (now - lastInteraction > IDLE_TIMEOUT) {
        isActive.value = false
        pomodoroRunning.value = false
        return
      }

      todaySeconds.value += TICK_INTERVAL
      trackSubjectTick()
      persist()
      persistSubjects()
      checkAchievements()
    }, TICK_INTERVAL * 1000)
  }

  function stopTick() {
    if (tickHandle) {
      clearInterval(tickHandle)
      tickHandle = null
    }
  }

  function startTracking() {
    checkNewDay()
    lastInteraction = Date.now()
    if (!isActive.value) {
      isActive.value = true
      startTick()
    }
  }

  function pauseTracking() {
    isActive.value = false
    if (pomodoroRunning.value) {
      pomodoroRunning.value = false
    }
  }

  function recordActivity() {
    lastInteraction = Date.now()
    if (!isActive.value) {
      isActive.value = true
      startTick()
    }
  }

  function isStudyRoute(path: string): boolean {
    return Object.keys(STUDY_ROUTES).some((r) => path.startsWith(r))
  }

  function setCurrentRoute(path: string) {
    currentRoute.value = path
  }

  // ── Init ──
  const savedGoal = Number(localStorage.getItem('study_goal') || '0')
  if (savedGoal >= 10 && savedGoal <= 480) goalMinutes.value = savedGoal
  checkNewDay()
  const saved = Number(localStorage.getItem(dateKey()) || '0')
  if (saved > 0) todaySeconds.value = saved
  loadSubjects()
  loadAchievements()
  recalcStreak()
  checkAchievements()

  return {
    // core
    todaySeconds,
    todayMinutes,
    progressPercent,
    goalMinutes,
    isGoalReached,
    isActive,
    streakDays,
    weeklyData,
    weeklyTotal,
    weeklyAvg,
    // pomodoro
    pomodoroPhase,
    pomodoroRemaining,
    pomodoroRunning,
    pomodoroDisplay,
    phaseLabel,
    phaseEmoji,
    focusCountToday,
    focusCount,
    startFocus,
    pausePomodoro,
    resumePomodoro,
    skipBreak,
    // subjects
    subjectBreakdown,
    // achievements
    unlockedAchievements,
    achievementDefs,
    // actions
    startTracking,
    pauseTracking,
    recordActivity,
    isStudyRoute,
    setGoal,
    setCurrentRoute,
  }
})
