import apiClient from './index'

export interface PathPhase {
  name: string
  duration_days: number
  tasks: DailyTask[]
}

export interface DailyTask {
  day: number
  subject: string
  topic: string
  task_type: 'review' | 'practice' | 'summary'
  estimated_minutes: number
  completed: boolean
}

export interface LearningPath {
  summary: string
  phases: PathPhase[]
  total_days: number
  progress: number
}

export function generatePath(diagnosisReportId: string): Promise<LearningPath> {
  return apiClient.post('/learning-path/generate', {
    diagnosis_report_id: diagnosisReportId,
  }) as any
}

export function adjustPath(pathData: {
  diagnosis_update?: Record<string, number>
  manual?: { pace: 'slower' | 'normal' | 'faster' }
}): Promise<LearningPath> {
  return apiClient.post('/learning-path/adjust', pathData) as any
}
