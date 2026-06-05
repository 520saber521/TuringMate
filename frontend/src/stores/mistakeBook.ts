import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Mistake {
  id: string
  questionContent: string
  subject: string
  knowledgeTags: string[]
  errorReason: string
  addedAt: number
  reviewedAt: number | null
  reviewed: boolean
}

const SUBJECTS = ['数据结构', '计组', '操作系统', '网络']

function generateId(): string {
  return `mk_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
}

export const useMistakeBookStore = defineStore('mistakeBook', () => {
  const mistakes = ref<Mistake[]>([])

  // ── Computed ──
  const totalCount = computed(() => mistakes.value.length)
  const unreviewedCount = computed(() => mistakes.value.filter(m => !m.reviewed).length)
  const reviewedCount = computed(() => mistakes.value.filter(m => m.reviewed).length)

  const bySubject = computed(() => {
    const map: Record<string, Mistake[]> = {}
    for (const s of SUBJECTS) map[s] = []
    for (const m of mistakes.value) {
      if (map[m.subject]) map[m.subject].push(m)
    }
    return map
  })

  const subjectsWithCounts = computed(() => {
    return SUBJECTS.map(s => ({
      subject: s,
      count: (bySubject.value[s] || []).length,
    })).filter(s => s.count > 0)
  })

  // ── Actions ──
  function addMistake(data: Omit<Mistake, 'id' | 'addedAt' | 'reviewedAt' | 'reviewed'>) {
    const mistake: Mistake = {
      ...data,
      id: generateId(),
      addedAt: Date.now(),
      reviewedAt: null,
      reviewed: false,
    }
    mistakes.value.unshift(mistake)
    persist()
    return mistake
  }

  function removeMistake(id: string) {
    mistakes.value = mistakes.value.filter(m => m.id !== id)
    persist()
  }

  function markReviewed(id: string) {
    const m = mistakes.value.find(x => x.id === id)
    if (m) {
      m.reviewed = true
      m.reviewedAt = Date.now()
      persist()
    }
  }

  function markUnreviewed(id: string) {
    const m = mistakes.value.find(x => x.id === id)
    if (m) {
      m.reviewed = false
      m.reviewedAt = null
      persist()
    }
  }

  function persist() {
    localStorage.setItem('mistake_book', JSON.stringify(mistakes.value))
  }

  function loadFromStorage() {
    try {
      const raw = localStorage.getItem('mistake_book')
      if (raw) mistakes.value = JSON.parse(raw)
    } catch { /* ignore */ }
  }

  // ── Init ──
  loadFromStorage()

  return {
    mistakes,
    totalCount,
    unreviewedCount,
    reviewedCount,
    bySubject,
    subjectsWithCounts,
    addMistake,
    removeMistake,
    markReviewed,
    markUnreviewed,
  }
})
