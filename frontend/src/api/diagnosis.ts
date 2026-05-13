import apiClient from './index'

export interface WeakPoint {
  subject: string
  topic: string
  score: number
  description?: string
}

export interface Recommendation {
  type: string
  title: string
  count: number
}

export interface DiagnosisReportResult {
  user_id: string
  scores: Record<string, number>
  weak_points: WeakPoint[]
  recommendations: Recommendation[]
}

export function getDiagnosisReport(userId = 'user_001') {
  return apiClient.get<DiagnosisReportResult>('/diagnosis/report', {
    params: { user_id: userId },
  })
}
