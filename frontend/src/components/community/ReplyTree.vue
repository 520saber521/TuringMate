<template>
  <div class="reply-tree">
    <div
      v-for="reply in topLevelReplies"
      :key="reply.id"
      class="reply-item"
      :class="{ accepted: reply.is_accepted }"
    >
      <div class="reply-body">
        <div class="reply-header">
          <span class="reply-user">{{ reply.user_id.slice(0, 8) }}</span>
          <span v-if="reply.is_accepted" class="accepted-badge">已采纳</span>
          <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
        </div>
        <p class="reply-content">{{ reply.content }}</p>
        <div class="reply-actions">
          <button
            v-if="!reply.is_accepted && showAccept"
            class="action-btn"
            @click="$emit('accept', reply.id)"
          >
            采纳
          </button>
          <button class="action-btn" @click="toggleReply(reply.id)">
            回复
          </button>
        </div>
        <!-- nested reply form -->
        <div v-if="replyingTo === reply.id" class="reply-form">
          <textarea
            v-model="replyText"
            rows="2"
            placeholder="输入回复..."
            class="reply-input"
          />
          <div class="reply-form-actions">
            <button class="cancel-btn" @click="replyingTo = null">取消</button>
            <button class="submit-btn" @click="submitReply(reply.id)">回复</button>
          </div>
        </div>
      </div>
      <!-- children -->
      <div v-if="children(reply.id).length" class="reply-children">
        <div
          v-for="child in children(reply.id)"
          :key="child.id"
          class="reply-item child-reply"
        >
          <div class="reply-body">
            <div class="reply-header">
              <span class="reply-user">{{ child.user_id.slice(0, 8) }}</span>
              <span class="reply-time">{{ formatTime(child.created_at) }}</span>
            </div>
            <p class="reply-content">{{ child.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ReplyItem } from '@/api/community'

const props = defineProps<{
  replies: ReplyItem[]
  showAccept?: boolean
}>()

const emit = defineEmits<{
  accept: [replyId: string]
  reply: [content: string, parentReplyId: string | null]
}>()

const replyingTo = ref<string | null>(null)
const replyText = ref('')

const topLevelReplies = computed(() =>
  props.replies.filter(r => !r.parent_reply_id)
)

function children(parentId: string): ReplyItem[] {
  return props.replies.filter(r => r.parent_reply_id === parentId)
}

function toggleReply(replyId: string) {
  replyingTo.value = replyingTo.value === replyId ? null : replyId
  replyText.value = ''
}

function submitReply(parentId: string) {
  if (replyText.value.trim()) {
    emit('reply', replyText.value.trim(), parentId)
    replyText.value = ''
    replyingTo.value = null
  }
}

function formatTime(ts: string | null): string {
  if (!ts) return ''
  const d = new Date(ts)
  return d.toLocaleDateString('zh-CN') + ' ' + d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.reply-item {
  border-left: 2px solid var(--td-component-border);
  padding-left: 12px;
  margin-bottom: 8px;
}
.reply-item.accepted {
  border-left-color: #52c41a;
}
.reply-children {
  margin-top: 8px;
  margin-left: 8px;
}
.reply-body {
  padding: 4px 0;
}
.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.reply-user {
  font-size: 12px;
  font-weight: 600;
  color: var(--td-text-color-primary);
}
.reply-time {
  font-size: 11px;
  color: var(--td-text-color-placeholder);
}
.accepted-badge {
  font-size: 10px;
  padding: 0 6px;
  border-radius: 4px;
  background: #52c41a;
  color: #fff;
}
.reply-content {
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  color: var(--td-text-color-primary);
}
.reply-actions {
  display: flex;
  gap: 12px;
  margin-top: 6px;
}
.action-btn {
  font-size: 11px;
  color: var(--td-brand-color);
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
}
.action-btn:hover {
  text-decoration: underline;
}
.reply-form {
  margin-top: 8px;
}
.reply-input {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--td-component-border);
  border-radius: 6px;
  font-size: 13px;
  resize: vertical;
  background: var(--td-bg-color-container);
  color: var(--td-text-color-primary);
}
.reply-form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 6px;
}
.cancel-btn {
  font-size: 12px;
  padding: 4px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: 4px;
  background: var(--td-bg-color-container);
  cursor: pointer;
}
.submit-btn {
  font-size: 12px;
  padding: 4px 12px;
  border: none;
  border-radius: 4px;
  background: var(--td-brand-color);
  color: #fff;
  cursor: pointer;
}
</style>
