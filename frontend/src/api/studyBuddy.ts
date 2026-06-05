import apiClient from './index'

export type BuddyRole = 'scholar' | 'hardworking' | 'discussion'
export type BuddyMode = 'debate' | 'collaborate' | 'quiz'

export interface BuddySession {
  session_id: string
  role: BuddyRole
  mode: BuddyMode
  greeting: string
  state: string
  messages: BuddyMessage[]
}

export interface BuddyMessage {
  role: 'user' | 'buddy'
  content: string
  buddy_role?: BuddyRole
}

export function startSession(role: BuddyRole, mode: BuddyMode, topic?: string): Promise<BuddySession> {
  return apiClient.post('/buddy/start', { role, mode, topic }) as any
}

export function sendMessage(sessionId: string, message: string): Promise<BuddyMessage> {
  return apiClient.post(`/buddy/${sessionId}/chat`, { message }) as any
}

export function getSession(sessionId: string): Promise<BuddySession> {
  return apiClient.get(`/buddy/${sessionId}`) as any
}

export function endSession(sessionId: string): Promise<{ summary: string }> {
  return apiClient.post(`/buddy/${sessionId}/end`) as any
}
