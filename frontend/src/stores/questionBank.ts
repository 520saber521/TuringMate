import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { listQuestions, getQuestionDetail, getYears, getTags, getSubjects, getByYear } from '@/api/questionBank'
import type { QuestionItem, QuestionDetail, SubjectInfo } from '@/api/questionBank'

export const useQuestionBankStore = defineStore('questionBank', () => {
  // State
  const items = ref<QuestionItem[]>([])
  const total = ref(0)
  const page = ref(1)
  const pageSize = ref(20)
  const loading = ref(false)
  const currentFilter = ref<{
    subject?: string
    tag?: string
    difficulty?: number
    year?: number
    keyword?: string
  }>({})

  const currentQuestion = ref<QuestionDetail | null>(null)
  const questionLoading = ref(false)
  const questionError = ref('')

  const years = ref<number[]>([])
  const tags = ref<string[]>([])
  const subjects = ref<SubjectInfo[]>([])

  // Computed
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasMore = computed(() => page.value < totalPages.value)

  // Actions
  async function fetchQuestions(filter?: typeof currentFilter.value) {
    loading.value = true
    if (filter) {
      currentFilter.value = { ...filter }
      page.value = 1
    }
    try {
      const res = await listQuestions({
        ...currentFilter.value,
        page: page.value,
        page_size: pageSize.value,
      })
      items.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function loadMore() {
    if (!hasMore.value || loading.value) return
    page.value++
    loading.value = true
    try {
      const res = await listQuestions({
        ...currentFilter.value,
        page: page.value,
        page_size: pageSize.value,
      })
      items.value.push(...res.items)
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchQuestionDetail(id: string) {
    questionLoading.value = true
    questionError.value = ''
    currentQuestion.value = null
    try {
      currentQuestion.value = await getQuestionDetail(id)
    } catch (e: any) {
      questionError.value = e?.userMessage || '题目加载失败，请稍后重试'
    } finally {
      questionLoading.value = false
    }
  }

  async function fetchYears() {
    try {
      const res = await getYears()
      years.value = res.years || []
    } catch { /* ignore */ }
  }

  async function fetchTags(subject?: string) {
    try {
      const res = await getTags(subject)
      tags.value = res.tags || []
    } catch { /* ignore */ }
  }

  async function fetchSubjects() {
    try {
      const res = await getSubjects()
      subjects.value = res.subjects || []
    } catch { /* ignore */ }
  }

  async function fetchByYear(year: number) {
    loading.value = true
    try {
      const res = await getByYear(year, { page: 1, page_size: 50 })
      items.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  function clearQuestion() {
    currentQuestion.value = null
    questionError.value = ''
  }

  return {
    items, total, page, pageSize, loading, currentFilter,
    currentQuestion, questionLoading, questionError,
    years, tags, subjects,
    totalPages, hasMore,
    fetchQuestions, loadMore, fetchQuestionDetail, clearQuestion,
    fetchYears, fetchTags, fetchSubjects, fetchByYear,
  }
})
