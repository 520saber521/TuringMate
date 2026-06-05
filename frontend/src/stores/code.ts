import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getChallenges, getChallenge, executeCode, submitAnswer, getExplanation } from '@/api/code'
import type { CodeChallenge, ExecutionResult } from '@/api/code'

export const useCodeStore = defineStore('code', () => {
  const challenges = ref<CodeChallenge[]>([])
  const currentChallenge = ref<CodeChallenge | null>(null)
  const executionResult = ref<ExecutionResult | null>(null)
  const explanation = ref('')
  const isLoading = ref(false)
  const error = ref('')

  async function fetchChallenges(params?: Record<string, string>) {
    isLoading.value = true
    error.value = ''
    try {
      const res = await getChallenges(params)
      challenges.value = res.challenges || []
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '加载失败'
    } finally { isLoading.value = false }
  }

  async function fetchDetail(id: string) {
    try {
      currentChallenge.value = await getChallenge(id)
      return currentChallenge.value
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '加载失败'
      return null
    }
  }

  async function runCode(body: { code: string; challenge_id?: string; language?: string }) {
    try {
      executionResult.value = await executeCode(body)
      return executionResult.value
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '执行失败'
      return null
    }
  }

  async function submit(challengeId: string, body: { code: string; challenge_id?: string; language?: string }) {
    try {
      executionResult.value = await submitAnswer(challengeId, body)
      return executionResult.value
    } catch (e: any) {
      error.value = e?.response?.data?.detail || '提交失败'
      return null
    }
  }

  async function fetchExplanation(id: string) {
    try {
      const res = await getExplanation(id)
      explanation.value = res.explanation || ''
      return explanation.value
    } catch { return '' }
  }

  function reset() {
    currentChallenge.value = null
    executionResult.value = null
    explanation.value = ''
    error.value = ''
  }

  return {
    challenges, currentChallenge, executionResult, explanation,
    isLoading, error,
    fetchChallenges, fetchDetail, runCode, submit, fetchExplanation, reset,
  }
})
