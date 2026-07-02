<template>
  <div class="cross-links">
    <h4 class="section-title">跨学科关联</h4>
    <div v-if="links.length === 0" class="empty-hint">暂无跨学科关联</div>
    <div
      v-for="link in links"
      :key="link.node_id"
      class="link-card"
      @click="$emit('navigate', link.node_id)"
    >
      <span class="link-subject-badge" :class="`subject-${link.subject}`">
        {{ SUBJECT_LABELS[link.subject] || link.subject }}
      </span>
      <span class="link-name">{{ link.node_name }}</span>
      <p class="link-relation">{{ link.relation }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CrossLink } from '@/api/knowledge'

defineProps<{
  links: CrossLink[]
}>()

defineEmits<{
  navigate: [nodeId: string]
}>()

const SUBJECT_LABELS: Record<string, string> = {
  ds: '数据结构', co: '计组', os: '操作系统', cn: '计算机网络',
}
</script>

<style scoped>
.section-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 12px;
}
.empty-hint {
  font-size: 13px;
  color: var(--td-text-color-placeholder);
  padding: 16px 0;
}
.link-card {
  padding: 10px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: box-shadow 0.15s;
}
.link-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.link-subject-badge {
  display: inline-block;
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 10px;
  margin-right: 8px;
  font-weight: 500;
}
.subject-ds { background: #e6f7ff; color: #1890ff; }
.subject-co { background: #fff7e6; color: #fa8c16; }
.subject-os { background: #f6ffed; color: #52c41a; }
.subject-cn { background: #f9f0ff; color: #722ed1; }
.link-name {
  font-size: 13px;
  font-weight: 500;
}
.link-relation {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--td-text-color-secondary);
}
</style>
