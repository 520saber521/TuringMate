/** Code challenge API — 代码实战模块. */
import apiClient from './index'

export interface CodeChallenge {
  id: string
  title: string
  description: string
  type: 'fill_gap' | 'debug' | 'trace' | 'design'
  difficulty: 'easy' | 'medium' | 'hard'
  subject: string
  topic: string
  constraints?: string[]
  examples?: { input: string; output: string }[]
  starter_code?: string
  status?: 'pending' | 'completed'
}

export interface ExecutionResult {
  execution_id?: string
  steps?: { step_no: number; description: string; variables?: Record<string, any> }[]
  output?: string
  error?: string
  evaluation?: { status: string; message?: string }
  passed?: boolean
}

export function getChallenges(params?: Record<string, string>) {
  return apiClient.get<{ challenges: CodeChallenge[]; count: number }>('/code/challenges', { params }).then(r => r.data)
}

export function getChallenge(id: string) {
  return apiClient.get<CodeChallenge>(`/code/challenges/${id}`).then(r => r.data)
}

export function executeCode(body: { code: string; challenge_id?: string; language?: string }) {
  return apiClient.post<ExecutionResult>('/code/execute', body).then(r => r.data)
}

export function submitAnswer(id: string, body: { code: string; challenge_id?: string; language?: string }) {
  return apiClient.post<ExecutionResult>(`/code/challenges/${id}/submit`, body).then(r => r.data)
}

export function getExplanation(id: string) {
  return apiClient.get<{ challenge_id: string; explanation: string }>(`/code/challenges/${id}/explanation`).then(r => r.data)
}
