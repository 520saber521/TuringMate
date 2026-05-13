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

export interface DiagnosisReport {
  user_id: string
  scores: Record<string, number>
  weak_points: WeakPoint[]
  recommendations: Recommendation[]
}
