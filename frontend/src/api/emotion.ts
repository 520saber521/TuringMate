import apiClient from './index'

export type EmotionType = 'frustrated' | 'anxious' | 'tired' | 'bored' | 'confident' | 'excited' | 'neutral'
export type TeachMode = 'confidence_build' | 'easy_review' | 'engage' | 'challenge' | 'deep_dive' | 'normal'

export interface EmotionState {
  session_id: string
  current_emotion: EmotionType
  confidence: number
  current_mode: TeachMode
  mode_override_prompt: string
}

export interface EmotionEvent {
  timestamp: string
  emotion: EmotionType
  confidence: number
  trigger_message: string
}

export function detectEmotion(sessionId: string, message: string): Promise<EmotionState> {
  return apiClient.post('/emotion/detect', { session_id: sessionId, message }) as any
}

export function getEmotionState(sessionId: string): Promise<EmotionState> {
  return apiClient.get(`/emotion/${sessionId}/state`) as any
}

export function getEmotionEvents(sessionId: string): Promise<EmotionEvent[]> {
  return apiClient.get(`/emotion/${sessionId}/events`) as any
}
