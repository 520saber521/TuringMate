<template>
  <div class="discussion-card" @click="$emit('click', discussion.id)">
    <div class="card-header">
      <span v-if="discussion.is_pinned" class="pin-badge">置顶</span>
      <span v-if="discussion.is_resolved" class="resolved-badge">已解决</span>
      <span class="card-title">{{ discussion.title }}</span>
    </div>
    <p class="card-content">{{ discussion.content.slice(0, 120) }}{{ discussion.content.length > 120 ? '...' : '' }}</p>
    <div class="card-footer">
      <div class="tags">
        <span v-for="tag in discussion.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <div class="stats">
        <span class="stat">
          <Heart :size="14" :class="{ liked: discussion.like_count > 0 }" />
          {{ discussion.like_count }}
        </span>
        <span class="stat">
          <MessageCircle :size="14" />
          {{ discussion.reply_count }}
        </span>
        <span class="stat text-xs text-gray-400">{{ formatTime(discussion.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Heart, MessageCircle } from 'lucide-vue-next'
import type { DiscussionItem } from '@/api/community'

defineProps<{
  discussion: DiscussionItem
}>()

defineEmits<{
  click: [id: string]
}>()

function formatTime(ts: string | null): string {
  if (!ts) return ''
  const d = new Date(ts)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.discussion-card {
  padding: 16px;
  border: 1px solid var(--td-component-border);
  border-radius: 10px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.discussion-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.pin-badge {
  font-size: 11px;
  padding: 0 6px;
  border-radius: 4px;
  background: #ff4d4f;
  color: #fff;
}
.resolved-badge {
  font-size: 11px;
  padding: 0 6px;
  border-radius: 4px;
  background: #52c41a;
  color: #fff;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
}
.card-content {
  font-size: 13px;
  color: var(--td-text-color-secondary);
  margin: 0 0 12px;
  line-height: 1.5;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.tags {
  display: flex;
  gap: 6px;
}
.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: var(--td-bg-color-secondarycontainer);
  color: var(--td-text-color-secondary);
}
.stats {
  display: flex;
  align-items: center;
  gap: 12px;
}
.stat {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: var(--td-text-color-placeholder);
}
.stat svg.liked {
  color: #ff4d4f;
  fill: #ff4d4f;
}
</style>
