/**
 * useChat - 苏格拉底式引导对话组合函数
 * 封装对话状态管理、API 调用、SSE 流式接收逻辑
 */
import { ref, computed, nextTick } from 'vue'
import { startChat, sendMessage, streamChat } from '@/api/chat'
import type { TutorStage } from '@/types/chat'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  stage?: TutorStage
  isStreaming?: boolean
}

export function useChat() {
  const sessionId = ref('')
  const messages = ref<ChatMessage[]>([])
  const currentStage = ref<TutorStage>('QUESTION')
  const isLoading = ref(false)
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  const messageCount = computed(() => messages.value.length)
  const isChatStarted = computed(() => !!sessionId.value)
  const isComplete = computed(() => currentStage.value === 'COMPLETE')

  let _abortController: AbortController | null = null

  /** 启动引导对话 */
  async function startGuidedChat(questionId: string) {
    isLoading.value = true
    error.value = null
    messages.value = []

    try {
      const result = await startChat(questionId)
      sessionId.value = result.session_id
      currentStage.value = result.stage

      messages.value.push({
        id: `msg_init_${Date.now()}`,
        role: 'assistant',
        content: result.first_message,
        timestamp: new Date().toISOString(),
        stage: result.stage,
      })
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || '启动对话失败'
      console.error('[useChat] startChat failed:', err)
    } finally {
      isLoading.value = false
    }
  }

  /** 发送用户消息（普通模式） */
  async function sendUserMessage(text: string) {
    if (!text.trim() || isLoading.value || !sessionId.value) return

    // 添加用户消息
    messages.value.push({
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    })

    isLoading.value = true
    error.value = null

    try {
      const result = await sendMessage(sessionId.value, text.trim())
      currentStage.value = result.stage as TutorStage

      messages.value.push({
        id: `msg_ai_${Date.now()}`,
        role: 'assistant',
        content: result.content,
        timestamp: new Date().toISOString(),
        stage: result.stage as TutorStage,
      })
    } catch (err: any) {
      error.value = err?.response?.data?.detail || err?.message || '发送消息失败'
      console.error('[useChat] sendMessage failed:', err)
    } finally {
      isLoading.value = false
    }
  }

  /** 发送用户消息（SSE 流式模式） */
  async function sendStreamingMessage(text: string) {
    if (!text.trim() || isStreaming.value || !sessionId.value) return

    // 添加用户消息
    messages.value.push({
      id: `msg_user_${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    })

    // 创建 AI 消息占位
    const aiMsgId = `msg_ai_${Date.now()}`
    messages.value.push({
      id: aiMsgId,
      role: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
      isStreaming: true,
    })

    isStreaming.value = true
    error.value = null

    _abortController = streamChat(
      sessionId.value,
      text.trim(),
      (chunk: string) => {
        // 更新最后一条 AI 消息
        const aiMsg = messages.value.find(m => m.id === aiMsgId)
        if (aiMsg) {
          aiMsg.content += chunk
        }
      },
    )

    // 监听完成（简单处理：流结束后标记非流式）
    // 注意：实际的流结束需要通过 SSE 事件来检测
    // 这里用 setTimeout 简化处理，后续可优化
    setTimeout(() => {
      const aiMsg = messages.value.find(m => m.id === aiMsgId)
      if (aiMsg) {
        aiMsg.isStreaming = false
      }
      isStreaming.value = false
    }, 15000) // 15 秒后强制结束流式
  }

  /** 停止流式输出 */
  function stopStreaming() {
    if (_abortController) {
      _abortController.abort()
      _abortController = null
    }
    isStreaming.value = false

    // 标记最后一条消息为非流式
    const lastMsg = messages.value[messages.value.length - 1]
    if (lastMsg?.isStreaming) {
      lastMsg.isStreaming = false
    }
  }

  /** 重置对话状态 */
  function resetChat() {
    stopStreaming()
    sessionId.value = ''
    messages.value = []
    currentStage.value = 'QUESTION'
    isLoading.value = false
    isStreaming.value = false
    error.value = null
  }

  /** 滚动到底部 */
  function scrollToBottom(container: HTMLElement | null) {
    nextTick(() => {
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    })
  }

  return {
    // State
    sessionId,
    messages,
    currentStage,
    isLoading,
    isStreaming,
    error,
    // Computed
    messageCount,
    isChatStarted,
    isComplete,
    // Actions
    startGuidedChat,
    sendUserMessage,
    sendStreamingMessage,
    stopStreaming,
    resetChat,
    scrollToBottom,
  }
}
