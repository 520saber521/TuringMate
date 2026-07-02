<template>
  <div v-if="topics.length" class="hot-topic-banner">
    <h4 class="banner-title">热门讨论</h4>
    <div class="topics-scroll">
      <div
        v-for="topic in topics"
        :key="topic.id"
        class="topic-card"
        @click="$emit('select', topic)"
      >
        <div class="topic-title">{{ topic.title }}</div>
        <p class="topic-summary">{{ topic.summary }}</p>
        <div class="topic-meta">
          {{ topic.discussion_ids.length }} 条相关讨论
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HotTopicItem } from '@/api/community'

defineProps<{
  topics: HotTopicItem[]
}>()

defineEmits<{
  select: [topic: HotTopicItem]
}>()
</script>

<style scoped>
.hot-topic-banner {
  margin-bottom: 20px;
}
.banner-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px;
}
.topics-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
}
.topic-card {
  flex: 0 0 240px;
  padding: 14px;
  border: 1px solid var(--td-component-border);
  border-radius: 10px;
  cursor: pointer;
  transition: box-shadow 0.15s;
  background: var(--td-bg-color-container);
}
.topic-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}
.topic-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 6px;
}
.topic-summary {
  font-size: 12px;
  color: var(--td-text-color-secondary);
  line-height: 1.5;
  margin: 0 0 8px;
}
.topic-meta {
  font-size: 11px;
  color: var(--td-text-color-placeholder);
}
</style>
