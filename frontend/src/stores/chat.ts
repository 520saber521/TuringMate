import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, TutorStage } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  const sessionId = ref('')
  const messages = ref<ChatMessage[]>([])
  const currentStage = ref<TutorStage>('QUESTION')
  const isLoading = ref(false)

  const messageCount = computed(() => messages.value.length)

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function setSession(id: string) {
    sessionId.value = id
    messages.value = []
    currentStage.value = 'QUESTION'
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  return { sessionId, messages, currentStage, isLoading, messageCount, addMessage, setSession, setLoading }
})
