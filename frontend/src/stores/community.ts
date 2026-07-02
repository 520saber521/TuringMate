import { defineStore } from 'pinia'
import { ref } from 'vue'
import { communityApi, type DiscussionItem, type DiscussionDetail, type HotTopicItem } from '@/api/community'

export const useCommunityStore = defineStore('community', () => {
  const discussions = ref<DiscussionItem[]>([])
  const total = ref(0)
  const currentDiscussion = ref<DiscussionDetail | null>(null)
  const hotTopics = ref<HotTopicItem[]>([])
  const loading = ref(false)

  async function fetchDiscussions(params?: {
    subject?: string; tag?: string; sort?: string; page?: number; page_size?: number
  }) {
    loading.value = true
    try {
      const res = await communityApi.listDiscussions(params)
      discussions.value = res.items
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchDiscussion(id: string) {
    loading.value = true
    try {
      currentDiscussion.value = await communityApi.getDiscussion(id)
    } finally {
      loading.value = false
    }
  }

  async function createDiscussion(data: { title: string; content: string; subject?: string; tags?: string[] }) {
    const disc = await communityApi.createDiscussion(data)
    discussions.value.unshift(disc)
    total.value++
    return disc
  }

  async function createReply(discussionId: string, content: string, parentReplyId?: string | null) {
    const reply = await communityApi.createReply(discussionId, { content, parent_reply_id: parentReplyId })
    if (currentDiscussion.value && currentDiscussion.value.id === discussionId) {
      currentDiscussion.value.replies.push(reply)
      currentDiscussion.value.reply_count++
    }
    return reply
  }

  async function acceptReply(replyId: string) {
    const reply = await communityApi.acceptReply(replyId)
    if (currentDiscussion.value) {
      currentDiscussion.value.resolved_reply_id = reply.id
      currentDiscussion.value.is_resolved = true
      currentDiscussion.value.replies = currentDiscussion.value.replies.map(item => ({
        ...item,
        is_accepted: item.id === reply.id,
      }))
    }
    return reply
  }

  async function toggleLike(discussionId: string) {
    const result = await communityApi.toggleLike(discussionId)
    const idx = discussions.value.findIndex(d => d.id === discussionId)
    if (idx !== -1) discussions.value[idx].like_count = result.like_count
    if (currentDiscussion.value?.id === discussionId) {
      currentDiscussion.value.like_count = result.like_count
    }
    return result
  }

  async function fetchHotTopics(limit = 5) {
    hotTopics.value = await communityApi.getHotTopics(limit)
  }

  return {
    discussions, total, currentDiscussion, hotTopics, loading,
    fetchDiscussions, fetchDiscussion, createDiscussion, createReply, acceptReply, toggleLike, fetchHotTopics,
  }
})
