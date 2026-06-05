import apiClient from './index'

export interface TraceStep {
  step_number: number
  title: string
  content: string
  confidence: number
  step_type: 'correct' | 'jump' | 'deviation' | 'stuck'
  gap_labels: string[]
}

export interface ThinkingPath {
  session_id: string
  steps: TraceStep[]
  conclusion: string
  final_state: 'mastered' | 'stuck' | 'in_progress'
}

export interface WeeklyReport {
  user_id: string
  total_sessions: number
  gap_stats: Record<string, number>
  radar_scores: { logic: number; completeness: number; speed: number }
  top_concerns: string[]
}

export function getThinkingPath(sessionId: string): Promise<ThinkingPath> {
  return apiClient.get(`/thinking/${sessionId}/path`) as any
}

export function getWeeklyReport(userId: string): Promise<WeeklyReport> {
  return apiClient.get(`/thinking/${userId}/report`) as any
}
