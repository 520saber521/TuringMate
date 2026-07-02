import apiClient from './index'

export interface KnowledgeNodeItem {
  id: string
  name: string
  difficulty: number
  prerequisites: string[]
}

export interface KnowledgeCategory {
  category: string
  nodes: KnowledgeNodeItem[]
}

export interface KnowledgeTreeResponse {
  subject: string
  tree: KnowledgeCategory[]
}

export interface KnowledgeNodeDetail {
  id: string
  name: string
  subject: string
  category: string
  difficulty: number
  prerequisites: string[]
  concept_explanation: string | null
  common_pitfalls: string[]
  related_question_ids: string[]
}

export interface CrossLink {
  node_id: string
  node_name: string
  subject: string
  relation: string
}

export interface SubjectInfo {
  id: string
  name: string
}

export const knowledgeApi = {
  getTree(subject = 'ds'): Promise<KnowledgeTreeResponse> {
    return apiClient.get(`/knowledge/tree?subject=${subject}`)
  },

  getNode(nodeId: string): Promise<KnowledgeNodeDetail> {
    return apiClient.get(`/knowledge/nodes/${nodeId}`)
  },

  getNodeQuestions(nodeId: string): Promise<{ node_id: string; questions: Array<{ id: string; content: string; difficulty: number }> }> {
    return apiClient.get(`/knowledge/nodes/${nodeId}/questions`)
  },

  getCrossLinks(nodeId: string): Promise<CrossLink[]> {
    return apiClient.get(`/knowledge/nodes/${nodeId}/cross-links`)
  },

  getSubjects(): Promise<{ subjects: SubjectInfo[] }> {
    return apiClient.get('/knowledge/subjects')
  },
}
