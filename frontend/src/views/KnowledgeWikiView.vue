<template>
  <div class="wiki-page">
    <div class="wiki-sidebar">
      <div class="subject-tabs">
        <button
          v-for="s in subjectList"
          :key="s.id"
          class="subject-tab"
          :class="{ active: store.currentSubject === s.id }"
          @click="store.fetchTree(s.id)"
        >
          {{ s.name }}
        </button>
      </div>
      <div class="tree-container">
        <KnowledgeTree
          v-if="store.tree"
          :tree="store.tree.tree"
          :active-node-id="activeNodeId"
          @select="onSelectNode"
        />
        <div v-else class="loading-hint">加载中...</div>
      </div>
    </div>
    <div class="wiki-main">
      <router-view />
      <div v-if="!activeNodeId" class="welcome">
        <h2>知识点 Wiki</h2>
        <p>选择左侧知识点查看详细内容、关联题目和跨学科联系</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useKnowledgeWikiStore } from '@/stores/knowledgeWiki'
import KnowledgeTree from '@/components/knowledge/KnowledgeTree.vue'

const store = useKnowledgeWikiStore()
const route = useRoute()
const router = useRouter()

const subjectList = [
  { id: 'ds', name: '数据结构' },
  { id: 'co', name: '计组' },
  { id: 'os', name: '操作系统' },
  { id: 'cn', name: '计算机网络' },
]

const activeNodeId = computed(() => route.params.nodeId as string || '')

function onSelectNode(nodeId: string) {
  router.push(`/wiki/${nodeId}`)
}

onMounted(async () => {
  await store.fetchTree(store.currentSubject)
})

watch(() => store.currentSubject, () => {
  // clear node selection when switching subjects
  if (activeNodeId.value) {
    router.push('/wiki')
  }
})
</script>

<style scoped>
.wiki-page {
  display: flex;
  height: calc(100vh - 56px);
}
.wiki-sidebar {
  width: 260px;
  border-right: 1px solid var(--td-component-border);
  display: flex;
  flex-direction: column;
  background: var(--td-bg-color-container);
  flex-shrink: 0;
}
.subject-tabs {
  display: flex;
  padding: 12px 8px;
  gap: 4px;
  border-bottom: 1px solid var(--td-component-border);
}
.subject-tab {
  flex: 1;
  font-size: 11px;
  padding: 6px 0;
  border: 1px solid var(--td-component-border);
  border-radius: 6px;
  background: var(--td-bg-color-container);
  cursor: pointer;
  text-align: center;
  color: var(--td-text-color-secondary);
  transition: all 0.15s;
}
.subject-tab.active {
  background: var(--td-brand-color);
  color: #fff;
  border-color: var(--td-brand-color);
}
.tree-container {
  flex: 1;
  overflow-y: auto;
}
.loading-hint {
  padding: 24px;
  text-align: center;
  color: var(--td-text-color-placeholder);
  font-size: 13px;
}
.wiki-main {
  flex: 1;
  overflow-y: auto;
  padding: 32px 40px;
}
.welcome {
  text-align: center;
  padding-top: 80px;
  color: var(--td-text-color-secondary);
}
.welcome h2 {
  font-size: 22px;
  margin-bottom: 8px;
  color: var(--td-text-color-primary);
}
</style>
