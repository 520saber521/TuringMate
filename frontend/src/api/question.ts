import apiClient from './index'

export interface QuestionParseResult {
  question_id: string
  subject: string
  knowledge_tags: string[]
  difficulty: number
  content: string
  image_url?: string
}

export function parseQuestionImage(file: File) {
  const formData = new FormData()
  formData.append('image', file)
  return apiClient.post<QuestionParseResult>('/question/parse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
