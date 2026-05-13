import apiClient from './index'

export type TutorStage = 'QUESTION' | 'HINT' | 'PROBE' | 'AFFIRM' | 'EXTEND' | 'COMPLETE'

export interface ChatStartResult {
  session_id: string
  first_message: string
  stage: TutorStage
}

export interface ChatMessageResult {
  session_id: string
  content: string
  stage: TutorStage
  hint_available: boolean
}

export function startChat(questionId: string) {
  return apiClient.post<ChatStartResult>('/chat/start', {
    question_id: questionId,
  })
}

export function sendMessage(sessionId: string, message: string) {
  return apiClient.post<ChatMessageResult>('/chat/message', {
    session_id: sessionId,
    message,
  })
}

// SSE 流式对话
export function streamChat(
  sessionId: string,
  message: string,
  onChunk: (text: string) => void,
): AbortController {
  const controller = new AbortController()
  fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
    signal: controller.signal,
  }).then(async (response) => {
    const reader = response.body?.getReader()
    if (!reader) return
    const decoder = new TextDecoder()
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const text = decoder.decode(value)
      // Parse SSE data lines
      for (const line of text.split('\n')) {
        if (line.startsWith('data: ')) {
          onChunk(line.slice(6))
        }
      }
    }
  })
  return controller
}
