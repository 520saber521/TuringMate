export interface Question {
  id: string
  subject: SubjectType
  knowledge_tags: string[]
  difficulty: number
  content: string
  image_url?: string
  solution_steps?: SolutionStep[]
}

export interface SolutionStep {
  step_no: number
  content: string
  hint?: string
}

export type SubjectType = '数据结构' | '计组' | '操作系统' | '网络'
