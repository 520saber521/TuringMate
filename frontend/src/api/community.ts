import apiClient from './index'

export interface DiscussionItem {
  id: string
  title: string
  content: string
  user_id: string
  subject: string
  tags: string[]
  like_count: number
  reply_count: number
  is_pinned: boolean
  is_resolved: boolean
  created_at: string | null
}

export interface DiscussionListResponse {
  items: DiscussionItem[]
  total: number
  page: number
  page_size: number
}

export interface DiscussionDetail extends DiscussionItem {
  resolved_reply_id: string | null
  replies: ReplyItem[]
}

export interface ReplyItem {
  id: string
  content: string
  discussion_id: string
  user_id: string
  parent_reply_id: string | null
  like_count: number
  is_accepted: boolean
  created_at: string | null
}

export interface HotTopicItem {
  id: number
  title: string
  summary: string
  discussion_ids: string[]
  created_at: string | null
}

export interface DiscussionCreate {
  title: string
  content: string
  subject?: string
  tags?: string[]
}

export interface ReplyCreate {
  content: string
  parent_reply_id?: string | null
}

export const communityApi = {
  listDiscussions(params?: {
    subject?: string
    tag?: string
    sort?: string
    page?: number
    page_size?: number
  }): Promise<DiscussionListResponse> {
    return apiClient.get('/community/discussions', { params })
  },

  getDiscussion(id: string): Promise<DiscussionDetail> {
    return apiClient.get(`/community/discussions/${id}`)
  },

  createDiscussion(data: DiscussionCreate): Promise<DiscussionItem> {
    return apiClient.post('/community/discussions', data)
  },

  createReply(discussionId: string, data: ReplyCreate): Promise<ReplyItem> {
    return apiClient.post(`/community/discussions/${discussionId}/replies`, data)
  },

  toggleLike(discussionId: string): Promise<{ liked: boolean; like_count: number }> {
    return apiClient.post(`/community/discussions/${discussionId}/like`)
  },

  acceptReply(replyId: string): Promise<ReplyItem> {
    return apiClient.post(`/community/replies/${replyId}/accept`)
  },

  getHotTopics(limit = 5): Promise<HotTopicItem[]> {
    return apiClient.get('/community/hot-topics', { params: { limit } })
  },
}
