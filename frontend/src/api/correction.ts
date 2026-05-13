import apiClient from './index'

export interface CorrectionStep {
  step_no: number
  content: string
  is_correct: boolean
  error_type?: string
  hint?: string
}

export interface CorrectionResult {
  correction_id: string
  question_id: string
  steps: CorrectionStep[]
  overall_feedback: string
}

export function analyzeCorrection(file: File, questionId?: string) {
  const formData = new FormData()
  formData.append('image', file)
  if (questionId) formData.append('question_id', questionId)
  return apiClient.post<CorrectionResult>('/correction/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
