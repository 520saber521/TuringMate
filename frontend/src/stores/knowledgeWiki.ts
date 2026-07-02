import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeApi, type KnowledgeTreeResponse, type KnowledgeNodeDetail, type CrossLink, type SubjectInfo } from '@/api/knowledge'

export const useKnowledgeWikiStore = defineStore('knowledgeWiki', () => {
  const subjects = ref<SubjectInfo[]>([])
  const currentSubject = ref('ds')
  const tree = ref<KnowledgeTreeResponse | null>(null)
  const currentNode = ref<KnowledgeNodeDetail | null>(null)
  const crossLinks = ref<CrossLink[]>([])
  const nodeQuestions = ref<Array<{ id: string; content: string; difficulty: number }>>([])
  const loading = ref(false)

  async function fetchSubjects() {
    const res = await knowledgeApi.getSubjects()
    subjects.value = res.subjects
  }

  async function fetchTree(subject: string) {
    loading.value = true
    try {
      currentSubject.value = subject
      tree.value = await knowledgeApi.getTree(subject)
    } finally {
      loading.value = false
    }
  }

  async function fetchNode(nodeId: string) {
    loading.value = true
    try {
      currentNode.value = await knowledgeApi.getNode(nodeId)
      const [links, qs] = await Promise.all([
        knowledgeApi.getCrossLinks(nodeId),
        knowledgeApi.getNodeQuestions(nodeId),
      ])
      crossLinks.value = links
      nodeQuestions.value = qs.questions
    } finally {
      loading.value = false
    }
  }

  const SUBJECT_LABELS: Record<string, string> = {
    ds: '数据结构', co: '计组', os: '操作系统', cn: '计算机网络',
  }

  return {
    subjects, currentSubject, tree, currentNode, crossLinks, nodeQuestions, loading,
    SUBJECT_LABELS,
    fetchSubjects, fetchTree, fetchNode,
  }
})
