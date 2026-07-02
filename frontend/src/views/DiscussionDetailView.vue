<template>
  <div class="discussion-detail" v-if="store.currentDiscussion">
    <!-- back -->
    <button class="back-btn" @click="$router.push('/community')">
      &larr; 返回社区
    </button>

    <!-- main post -->
    <div class="main-post">
      <div class="post-header">
        <h1 class="post-title">{{ store.currentDiscussion.title }}</h1>
        <div class="post-meta">
          <span v-if="store.currentDiscussion.is_pinned" class="badge pin">置顶</span>
          <span v-if="store.currentDiscussion.is_resolved" class="badge resolved">已解决</span>
          <span class="post-time">{{ formatTime(store.currentDiscussion.created_at) }}</span>
        </div>
      </div>
      <p class="post-content">{{ store.currentDiscussion.content }}</p>
      <div class="post-tags">
        <span v-for="tag in store.currentDiscussion.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <div class="post-actions">
        <button class="action-btn" @click="handleLike">
          <Heart :size="15" :fill="liked ? '#ff4d4f' : 'none'" :color="liked ? '#ff4d4f' : undefined" />
          {{ store.currentDiscussion.like_count }}
        </button>
      </div>
    </div>

    <!-- replies -->
    <section class="replies-section">
      <h3>回复 ({{ store.currentDiscussion.reply_count }})</h3>
      <ReplyTree
        :replies="store.currentDiscussion.replies"
        :show-accept="true"
        @accept="handleAccept"
        @reply="handleReply"
      />
    </section>

    <!-- reply form -->
    <div class="reply-form-bottom">
      <textarea
        v-model="replyText"
        rows="3"
        placeholder="写下你的回复..."
        class="reply-textarea"
      />
      <button
        class="reply-submit-btn"
        :disabled="!replyText.trim()"
        @click="handleReply(replyText, null)"
      >
        回复
      </button>
    </div>
  </div>

  <div v-else-if="store.loading" class="loading-state">加载中...</div>
  <div v-else class="empty-state">帖子不存在</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCommunityStore } from '@/stores/community'
import ReplyTree from '@/components/community/ReplyTree.vue'
import { Heart } from 'lucide-vue-next'

const store = useCommunityStore()
const route = useRoute()
const replyText = ref('')
const liked = ref(false)

async function handleLike() {
  const result = await store.toggleLike(store.currentDiscussion!.id)
  liked.value = result.liked
}

async function handleAccept(replyId: string) {
  await store.acceptReply(replyId)
}

async function handleReply(content: string, parentReplyId: string | null) {
  if (!content.trim()) return
  await store.createReply(store.currentDiscussion!.id, content, parentReplyId)
  replyText.value = ''
}

function formatTime(ts: string | null): string {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
  const id = route.params.discussionId as string
  if (id) await store.fetchDiscussion(id)
})
</script>

<style scoped>
.discussion-detail {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 16px;
}
.back-btn {
  font-size: 13px;
  background: none;
  border: none;
  color: var(--td-brand-color);
  cursor: pointer;
  padding: 0;
  margin-bottom: 16px;
}
.main-post {
  padding: 20px;
  border: 1px solid var(--td-component-border);
  border-radius: 12px;
  margin-bottom: 24px;
}
.post-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.badge {
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 4px;
  color: #fff;
}
.badge.pin {
  background: #ff4d4f;
}
.badge.resolved {
  background: #52c41a;
}
.post-time {
  font-size: 12px;
  color: var(--td-text-color-placeholder);
}
.post-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--td-text-color-primary);
  margin: 0 0 12px;
}
.post-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}
.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--td-bg-color-secondarycontainer);
}
.post-actions {
  display: flex;
  gap: 12px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  color: var(--td-text-color-secondary);
}
.action-btn:hover {
  background: var(--td-bg-color-container-hover);
}

.replies-section h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 16px;
}
.reply-form-bottom {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--td-component-border);
}
.reply-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  font-size: 13px;
  resize: vertical;
  font-family: inherit;
  background: var(--td-bg-color-container);
  color: var(--td-text-color-primary);
  box-sizing: border-box;
}
.reply-submit-btn {
  margin-top: 8px;
  padding: 8px 20px;
  background: var(--td-brand-color);
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  float: right;
}
.reply-submit-btn:disabled {
  opacity: 0.5;
  cursor: default;
}
.loading-state, .empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--td-text-color-placeholder);
}
</style>
