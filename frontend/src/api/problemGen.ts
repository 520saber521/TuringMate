import apiClient from './index'

export interface VariantRequest {
  subject: string
  knowledge_tags: string[]
  difficulty?: number
  source_question?: string
}

export interface ValidateRequest {
  variant_id: string
  user_answer: string
}

export interface VariantQuestion {
  id: string
  content: string
  subject: string
  knowledge_tags: string[]
  difficulty: number
  options?: string[]
}

export interface GenerateResponse {
  source_question: VariantQuestion
  variants: VariantQuestion[]
}

export interface ValidateResponse {
  variant_id: string
  is_correct: boolean
  mastery_level: '未掌握' | '部分掌握' | '已掌握'
  feedback: string
  next_variant?: VariantQuestion
}

export interface Template {
  id: string
  subject: string
  topic: string
  difficulty: number
  param_names: string[]
}

export function generateVariants(params: VariantRequest): Promise<GenerateResponse> {
  return apiClient.post('/problem-gen/generate', params) as any
}

export function validateAnswer(params: ValidateRequest): Promise<ValidateResponse> {
  return apiClient.post('/problem-gen/validate', params) as any
}

export function getTemplates(): Promise<Template[]> {
  return apiClient.get('/problem-gen/templates') as any
}
