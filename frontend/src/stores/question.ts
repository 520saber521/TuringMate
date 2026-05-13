import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Question } from '@/types/question'

export const useQuestionStore = defineStore('question', () => {
  const currentQuestion = ref<Question | null>(null)

  function setQuestion(q: Question) {
    currentQuestion.value = q
  }

  function clearQuestion() {
    currentQuestion.value = null
  }

  return { currentQuestion, setQuestion, clearQuestion }
})
