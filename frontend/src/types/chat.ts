export type TutorStage = 'QUESTION' | 'HINT' | 'PROBE' | 'AFFIRM' | 'EXTEND' | 'COMPLETE'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  stage?: TutorStage
}

export interface ChatSession {
  id: string
  question_id: string
  status: 'active' | 'completed' | 'abandoned'
  messages: ChatMessage[]
  current_stage: TutorStage
}
