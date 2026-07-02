<template>
  <div class="knowledge-tree">
    <div
      v-for="category in tree"
      :key="category.category"
      class="tree-category"
    >
      <div class="category-title">{{ category.category }}</div>
      <div
        v-for="node in category.nodes"
        :key="node.id"
        class="tree-node"
        :class="{ active: activeNodeId === node.id }"
        @click="$emit('select', node.id)"
      >
        <div class="node-name">{{ node.name }}</div>
        <div class="node-meta">
          <span class="difficulty" :class="`d-${node.difficulty}`">
            {{ '★'.repeat(node.difficulty) }}{{ '☆'.repeat(5 - node.difficulty) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { KnowledgeCategory } from '@/api/knowledge'

defineProps<{
  tree: KnowledgeCategory[]
  activeNodeId?: string
}>()

defineEmits<{
  select: [nodeId: string]
}>()
</script>

<style scoped>
.knowledge-tree {
  padding: 4px 0;
}
.tree-category {
  margin-bottom: 8px;
}
.category-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--td-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 12px 4px;
}
.tree-node {
  padding: 8px 12px 8px 16px;
  cursor: pointer;
  border-radius: 6px;
  margin: 2px 8px;
  transition: background 0.15s;
}
.tree-node:hover {
  background: var(--td-bg-color-container-hover);
}
.tree-node.active {
  background: var(--td-brand-color-light);
  color: var(--td-brand-color);
}
.node-name {
  font-size: 13px;
  font-weight: 500;
}
.node-meta {
  margin-top: 2px;
}
.difficulty {
  font-size: 10px;
  letter-spacing: 1px;
}
.d-1, .d-2 { color: #52c41a; }
.d-3 { color: #faad14; }
.d-4, .d-5 { color: #ff4d4f; }
</style>
