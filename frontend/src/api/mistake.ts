import apiClient from './index'

export interface MistakeItem {
  id: string
  question_id: string | null
  user_answer: string | null
  error_type: string
  knowledge_tags: string[]
  reviewed: number
  reviewed_at: string | null
  created_at: string | null
}

export function listMistakes(params?: { subject?: string; reviewed?: number; limit?: number }) {
  return apiClient.get('/mistakes', { params }) as Promise<{ items: MistakeItem[]; total: number }>
}

export function addMistake(data: { question_id: string; user_answer?: string; error_type?: string; knowledge_tags?: string[] }) {
  return apiClient.post('/mistakes', data) as Promise<{ id: string; message: string }>
}

export function markReviewed(id: string) {
  return apiClient.put(`/mistakes/${id}/review`) as Promise<{ id: string; reviewed: boolean }>
}

export function markUnreviewed(id: string) {
  return apiClient.put(`/mistakes/${id}/unreview`) as Promise<{ id: string; reviewed: boolean }>
}

export function deleteMistake(id: string) {
  return apiClient.delete(`/mistakes/${id}`) as Promise<{ id: string; deleted: boolean }>
}
