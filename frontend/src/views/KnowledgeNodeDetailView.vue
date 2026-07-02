<template>
  <div class="node-detail" v-if="store.currentNode">
    <h1 class="node-title">{{ store.currentNode.name }}</h1>
    <div class="node-meta">
      <span class="node-category">{{ store.currentNode.category }}</span>
      <span class="node-difficulty" :class="`d-${store.currentNode.difficulty}`">
        难度: {{ '★'.repeat(store.currentNode.difficulty) }}
      </span>
    </div>

    <!-- concept -->
    <section class="detail-section" v-if="store.currentNode.concept_explanation">
      <h3>概念解释</h3>
      <p class="concept-text">{{ store.currentNode.concept_explanation }}</p>
    </section>

    <!-- prerequisites -->
    <section class="detail-section" v-if="store.currentNode.prerequisites.length">
      <h3>前置知识点</h3>
      <div class="prereq-list">
        <span
          v-for="pid in store.currentNode.prerequisites"
          :key="pid"
          class="prereq-tag"
          @click="$router.push(`/wiki/${pid}`)"
        >
          {{ pid }}
        </span>
      </div>
    </section>

    <!-- pitfalls -->
    <section class="detail-section" v-if="store.currentNode.common_pitfalls.length">
      <h3>常见误区</h3>
      <ul class="pitfall-list">
        <li v-for="(p, i) in store.currentNode.common_pitfalls" :key="i">{{ p }}</li>
      </ul>
    </section>

    <!-- related questions -->
    <section class="detail-section">
      <h3>关联题目</h3>
      <div v-if="store.nodeQuestions.length" class="question-list">
        <div
          v-for="q in store.nodeQuestions"
          :key="q.id"
          class="question-item"
          @click="$router.push(`/bank/question/${q.id}`)"
        >
          <span class="q-diff" :class="`d-${q.difficulty}`">L{{ q.difficulty }}</span>
          <span class="q-content">{{ q.content }}</span>
        </div>
      </div>
      <div v-else class="empty-hint">暂无关联题目</div>
    </section>

    <!-- cross links -->
    <section class="detail-section">
      <CrossSubjectLinks
        :links="store.crossLinks"
        @navigate="id => $router.push(`/wiki/${id}`)"
      />
    </section>
  </div>

  <div v-else-if="store.loading" class="loading-state">加载中...</div>
  <div v-else class="empty-state">知识点不存在</div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useKnowledgeWikiStore } from '@/stores/knowledgeWiki'
import CrossSubjectLinks from '@/components/knowledge/CrossSubjectLinks.vue'

const store = useKnowledgeWikiStore()
const route = useRoute()

async function load() {
  const nodeId = route.params.nodeId as string
  if (nodeId) {
    await store.fetchNode(nodeId)
  }
}

onMounted(load)
watch(() => route.params.nodeId, load)
</script>

<style scoped>
.node-detail {
  max-width: 720px;
}
.node-title {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 8px;
}
.node-meta {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}
.node-category {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 12px;
  background: var(--td-bg-color-secondarycontainer);
  color: var(--td-text-color-secondary);
}
.node-difficulty {
  font-size: 12px;
}
.d-1, .d-2 { color: #52c41a; }
.d-3 { color: #faad14; }
.d-4, .d-5 { color: #ff4d4f; }

.detail-section {
  margin-bottom: 28px;
}
.detail-section h3 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--td-component-border);
}
.concept-text {
  font-size: 14px;
  line-height: 1.8;
  color: var(--td-text-color-primary);
}

.prereq-list {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.prereq-tag {
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 14px;
  background: var(--td-brand-color-light);
  color: var(--td-brand-color);
  cursor: pointer;
}
.prereq-tag:hover {
  background: var(--td-brand-color);
  color: #fff;
}

.pitfall-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  line-height: 1.8;
  color: var(--td-text-color-primary);
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.question-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid var(--td-component-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
}
.question-item:hover {
  background: var(--td-bg-color-container-hover);
}
.q-diff {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}
.q-content {
  font-size: 13px;
  line-height: 1.5;
}
.empty-hint, .loading-state, .empty-state {
  font-size: 13px;
  color: var(--td-text-color-placeholder);
  padding: 24px 0;
}
</style>
