import apiClient from './index'

export interface QuestionItem {
  id: string
  subject: string
  knowledge_tags: string[]
  difficulty: number
  content: string
  year?: number
  exam_paper: string
  source_type: string
}

export interface QuestionDetail {
  id: string
  subject: string
  knowledge_tags: string[]
  difficulty: number
  content: string
  image_url: string
  solution_steps: StepItem[]
  year?: number
  exam_paper: string
  source_type: string
  ai_analysis?: string
}

export interface StepItem {
  step_no: number
  content: string
  hint?: string
}

export interface QuestionListResponse {
  items: QuestionItem[]
  total: number
  page: number
  page_size: number
}

export interface SubjectInfo {
  id: string
  name: string
  icon: string
}

export function listQuestions(params: {
  subject?: string
  tag?: string
  difficulty?: number
  year?: number
  keyword?: string
  page?: number
  page_size?: number
}) {
  return apiClient.get('/question/questions', { params }) as Promise<QuestionListResponse>
}

export function searchQuestions(q: string, subject?: string, limit?: number) {
  return apiClient.get('/question/questions/search', { params: { q, subject, limit } }) as Promise<QuestionItem[]>
}

export function getQuestionDetail(id: string) {
  return apiClient.get(`/question/questions/${id}`) as Promise<QuestionDetail>
}

export function getYears() {
  return apiClient.get('/question/questions/years') as Promise<{ years: number[] }>
}

export function getByYear(year: number, params?: { subject?: string; page?: number; page_size?: number }) {
  return apiClient.get(`/question/questions/by-year/${year}`, { params }) as Promise<QuestionListResponse>
}

export function getTags(subject?: string) {
  return apiClient.get('/question/questions/tags', { params: { subject } }) as Promise<{ tags: string[] }>
}

export function getSubjects() {
  return apiClient.get('/question/subjects') as Promise<{ subjects: SubjectInfo[] }>
}
