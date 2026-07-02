import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { listMistakes as apiList, addMistake as apiAdd, markReviewed as apiReview, markUnreviewed as apiUnreview, deleteMistake as apiDelete } from '@/api/mistake'
import type { MistakeItem } from '@/api/mistake'

export interface Mistake {
  id: string
  questionContent: string
  subject: string
  knowledgeTags: string[]
  errorReason: string
  addedAt: number
  reviewedAt: number | null
  reviewed: boolean
  questionId: string | null
}

const SUBJECTS = ['数据结构', '计组', '操作系统', '计算机网络']

export const useMistakeBookStore = defineStore('mistakeBook', () => {
  const mistakes = ref<Mistake[]>([])
  const loading = ref(false)

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
  async function fetchMistakes() {
    loading.value = true
    try {
      const res = await apiList({ limit: 200 })
      mistakes.value = (res.items || []).map(toLocal)
    } catch {
      // fallback to localStorage if offline
      loadFromStorage()
    } finally {
      loading.value = false
    }
  }

  async function addMistake(data: {
    question_id?: string
    questionContent?: string
    subject?: string
    knowledgeTags?: string[]
    errorReason?: string
  }) {
    const { useAuthStore } = await import('@/stores/auth')
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      if (data.questionContent) {
        addLocalMistake(data)
        return true
      }
      return false
    }

    try {
      await apiAdd({
        question_id: data.question_id || '',
        knowledge_tags: data.knowledgeTags || [],
      })
      await fetchMistakes()
      return true
    } catch {
      if (data.questionContent) {
        addLocalMistake(data)
        return true
      }
      return false
    }
  }

  function addLocalMistake(data: {
    question_id?: string
    questionContent?: string
    subject?: string
    knowledgeTags?: string[]
    errorReason?: string
  }) {
    const id = data.question_id || `local-${Date.now()}`
    mistakes.value.unshift({
      id,
      questionId: data.question_id || null,
      questionContent: data.questionContent || '',
      subject: data.subject || '未知',
      knowledgeTags: data.knowledgeTags || [],
      errorReason: data.errorReason || '待复习',
      addedAt: Date.now(),
      reviewedAt: null,
      reviewed: false,
    })
    persist()
  }

  async function removeMistake(id: string) {
    try {
      await apiDelete(id)
      mistakes.value = mistakes.value.filter(m => m.id !== id)
    } catch {
      // fallback: remove locally
      mistakes.value = mistakes.value.filter(m => m.id !== id)
      persist()
    }
  }

  async function markReviewed(id: string) {
    try {
      await apiReview(id)
      const m = mistakes.value.find(x => x.id === id)
      if (m) {
        m.reviewed = true
        m.reviewedAt = Date.now()
      }
    } catch { /* ignore */ }
  }

  async function markUnreviewed(id: string) {
    try {
      await apiUnreview(id)
      const m = mistakes.value.find(x => x.id === id)
      if (m) {
        m.reviewed = false
        m.reviewedAt = null
      }
    } catch { /* ignore */ }
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

  // ── Helpers ──
  function toLocal(item: MistakeItem): Mistake {
    // Determine subject from knowledge_tags or default
    let subject = '数据结构'
    const tags = item.knowledge_tags || []
    if (tags.length > 0) {
      const tagMap: Record<string, string> = {
        '线性表': '数据结构', '链表操作': '数据结构', '二叉树': '数据结构',
        '数制与编码': '计组', 'Cache映射': '计组',
        '进程同步': '操作系统',
        'TCP协议': '计算机网络',
      }
      for (const t of tags) {
        if (tagMap[t]) { subject = tagMap[t]; break }
      }
    }

    return {
      id: item.id,
      questionContent: '',
      subject,
      knowledgeTags: item.knowledge_tags || [],
      errorReason: item.error_type || '',
      addedAt: item.created_at ? new Date(item.created_at).getTime() : Date.now(),
      reviewedAt: item.reviewed_at ? new Date(item.reviewed_at).getTime() : null,
      reviewed: item.reviewed === 1,
      questionId: item.question_id,
    }
  }

  // ── Init: try backend first, fallback to localStorage ──
  fetchMistakes()

  return {
    mistakes, loading,
    totalCount, unreviewedCount, reviewedCount,
    bySubject, subjectsWithCounts,
    addMistake, removeMistake, markReviewed, markUnreviewed,
    fetchMistakes,
  }
})
