<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionBankStore } from '@/stores/questionBank'
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight, X } from 'lucide-vue-next'
import TopicTag from '@/components/question/TopicTag.vue'

const route = useRoute()
const router = useRouter()
const store = useQuestionBankStore()

const SUBJECT_LABELS: Record<string, string> = {
  '数据结构': '数据结构', '计组': '计算机组成原理',
  '操作系统': '操作系统', '计算机网络': '计算机网络',
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: '基础', 2: '简单', 3: '中等', 4: '较难', 5: '困难',
}

onMounted(() => {
  store.fetchTags(route.query.subject as string)
  store.fetchQuestions({
    subject: route.query.subject as string,
    tag: route.query.tag as string,
    difficulty: route.query.difficulty ? Number(route.query.difficulty) : undefined,
    keyword: route.query.keyword as string,
    year: route.query.year ? Number(route.query.year) : undefined,
  })
})

function viewQuestion(id: string) {
  router.push(`/bank/question/${id}`)
}

function goPage(p: number) {
  if (p < 1 || p > store.totalPages) return
  store.page = p
  store.fetchQuestions()
}

function clearFilters() {
  router.replace({ query: {} })
  store.fetchQuestions({})
}

const hasFilters = computed(() => {
  const q = route.query
  return !!(q.subject || q.tag || q.difficulty || q.keyword || q.year)
})
</script>

<template>
  <div class="question-list-view">
    <!-- Header with result count -->
    <div class="list-header">
      <div>
        <h1 class="list-title">题目列表</h1>
        <p class="list-count" v-if="!store.loading">共 {{ store.total }} 道题目</p>
      </div>
      <button v-if="hasFilters" class="clear-btn" @click="clearFilters">
        <X :size="14" /> 清除筛选
      </button>
    </div>

    <!-- Active Filters -->
    <div class="active-filters" v-if="hasFilters">
      <span class="filter-chip purple" v-if="route.query.subject">
        {{ SUBJECT_LABELS[route.query.subject as string] || route.query.subject }}
      </span>
      <span class="filter-chip blue" v-if="route.query.tag">{{ route.query.tag }}</span>
      <span class="filter-chip amber" v-if="route.query.difficulty">
        难度 {{ route.query.difficulty }}
      </span>
      <span class="filter-chip green" v-if="route.query.keyword">"{{ route.query.keyword }}"</span>
      <span class="filter-chip slate" v-if="route.query.year">{{ route.query.year }}年真题</span>
    </div>

    <!-- Question List -->
    <div class="question-list" v-if="store.items.length">
      <button
        v-for="item in store.items"
        :key="item.id"
        class="question-item"
        @click="viewQuestion(item.id)"
      >
        <div class="question-item__top">
          <div class="question-item__tags">
            <span class="subject-badge">{{ item.subject }}</span>
            <span class="year-badge" v-if="item.year">{{ item.year }}年</span>
            <span class="diff-badge" :class="`diff-${item.difficulty}`">
              {{ DIFFICULTY_LABELS[item.difficulty] || item.difficulty }}
            </span>
          </div>
        </div>
        <p class="question-item__content">{{ item.content.slice(0, 120) }}{{ item.content.length > 120 ? '...' : '' }}</p>
        <div class="question-item__bottom" v-if="item.knowledge_tags?.length">
          <TopicTag v-for="tag in item.knowledge_tags.slice(0, 3)" :key="tag" :label="tag" />
        </div>
      </button>
    </div>

    <!-- Empty State -->
    <div class="empty" v-else-if="!store.loading">
      <p class="empty__text">暂无题目</p>
      <button class="empty__btn" @click="clearFilters">清除筛选条件</button>
    </div>

    <!-- Loading -->
    <div class="loading" v-if="store.loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="store.totalPages > 1">
      <button :disabled="store.page <= 1" @click="goPage(store.page - 1)">
        <ChevronLeft :size="16" /> 上一页
      </button>
      <span class="page-info">{{ store.page }} / {{ store.totalPages }}</span>
      <button :disabled="store.page >= store.totalPages" @click="goPage(store.page + 1)">
        下一页 <ChevronRight :size="16" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.question-list-view {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-bottom: 2rem;
}

.list-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
}
.list-title { font-size: 1.35rem; font-weight: 700; color: #1f2937; }
.list-count { font-size: 0.85rem; color: #9ca3af; margin-top: 0.2rem; }
.clear-btn {
  display: flex; align-items: center; gap: 0.3rem;
  padding: 0.4rem 0.75rem; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08); background: white;
  color: #6b7280; font-size: 0.8rem; cursor: pointer; font-family: inherit;
  transition: all 0.15s;
}
.clear-btn:hover { border-color: #ef4444; color: #ef4444; }

.active-filters {
  display: flex; flex-wrap: wrap; gap: 0.5rem;
}
.filter-chip {
  font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.6rem;
  border-radius: 999px; display: inline-flex; align-items: center;
}
.filter-chip.purple { background: rgba(139,92,246,0.1); color: #7c3aed; }
.filter-chip.blue { background: rgba(14,165,233,0.1); color: #0ea5e9; }
.filter-chip.amber { background: rgba(245,158,11,0.1); color: #d97706; }
.filter-chip.green { background: rgba(16,185,129,0.1); color: #059669; }
.filter-chip.slate { background: #f1f5f9; color: #64748b; }

.question-list {
  display: flex; flex-direction: column; gap: 0.5rem;
}

.question-item {
  display: flex; flex-direction: column; gap: 0.5rem;
  padding: 1.25rem; border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.06); background: white;
  text-align: left;
  cursor: pointer; transition: all 0.15s;
  font-family: inherit;
}
.question-item:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  border-color: rgba(139,92,246,0.2);
}
.question-item__top { display: flex; align-items: center; justify-content: space-between; }
.question-item__tags { display: flex; align-items: center; gap: 0.4rem; }
.subject-badge {
  font-size: 0.72rem; font-weight: 600; padding: 0.15rem 0.5rem;
  border-radius: 6px; background: rgba(139,92,246,0.08); color: #7c3aed;
}
.year-badge {
  font-size: 0.72rem; padding: 0.15rem 0.5rem;
  border-radius: 6px; background: #f1f5f9; color: #64748b;
}
.diff-badge {
  font-size: 0.72rem; padding: 0.15rem 0.5rem; border-radius: 6px;
}
.diff-2 { background: #dcfce7; color: #16a34a; }
.diff-3 { background: #fef3c7; color: #d97706; }
.diff-4 { background: #fee2e2; color: #dc2626; }
.diff-5 { background: #fce7f3; color: #db2777; }

.question-item__content {
  font-size: 0.88rem; color: #374151; line-height: 1.6; margin: 0;
}
.question-item__bottom {
  display: flex; flex-wrap: wrap; gap: 0.35rem;
}

/* Empty */
.empty {
  text-align: center; padding: 3rem 1rem;
}
.empty__text { color: #9ca3af; font-size: 1rem; margin-bottom: 1rem; }
.empty__btn {
  padding: 0.5rem 1.25rem; border-radius: 12px;
  border: none; background: linear-gradient(135deg, #7c3aed, #8b5cf6);
  color: white; font-size: 0.85rem; font-weight: 600; cursor: pointer; font-family: inherit;
}

/* Loading */
.loading { text-align: center; padding: 3rem; color: #9ca3af; }
.loading-spinner {
  width: 32px; height: 32px; border: 3px solid #e5e7eb;
  border-top-color: #8b5cf6; border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 0.75rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Pagination */
.pagination {
  display: flex; align-items: center; justify-content: center; gap: 1rem;
  padding: 1rem 0;
}
.pagination button {
  display: flex; align-items: center; gap: 0.3rem;
  padding: 0.5rem 1rem; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08); background: white;
  color: #374151; font-size: 0.85rem; cursor: pointer; font-family: inherit;
  transition: all 0.15s;
}
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination button:not(:disabled):hover { border-color: #8b5cf6; color: #8b5cf6; }
.page-info { font-size: 0.85rem; color: #6b7280; font-weight: 500; }
</style>
