import apiClient from './index'

export interface VisualStep {
  step_no: number
  line: number
  description: string
  variables: Record<string, unknown>
  visual_state: Record<string, unknown>
}

export interface VisualizeResult {
  execution_id: string
  language: string
  steps: VisualStep[]
  total_steps: number
}

export function executeAndVisualize(code: string, language = 'python') {
  return apiClient.post<VisualizeResult>('/visualize/execute', {
    code,
    language,
  })
}
