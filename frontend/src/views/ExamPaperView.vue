<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionBankStore } from '@/stores/questionBank'
import { FileText, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import TopicTag from '@/components/question/TopicTag.vue'

const route = useRoute()
const router = useRouter()
const store = useQuestionBankStore()

const yearParam = computed(() => Number(route.params.year))

onMounted(() => {
  store.fetchYears()
  store.fetchByYear(yearParam.value)
})

watch(() => route.params.year, (newYear) => {
  if (newYear) store.fetchByYear(Number(newYear))
})

function viewQuestion(id: string) {
  router.push(`/bank/question/${id}`)
}

function goYear(y: number) {
  router.push(`/bank/exam/${y}`)
}

const DIFFICULTY_LABELS: Record<number, string> = {
  1: '基础', 2: '简单', 3: '中等', 4: '较难', 5: '困难',
}
</script>

<template>
  <div class="exam-view">
    <!-- Back -->
    <button class="back-btn" @click="router.push('/bank')">
      <ChevronLeft :size="16" /> 返回题库
    </button>

    <!-- Year Selector -->
    <div class="year-bar">
      <h1 class="year-title">{{ yearParam }}年408真题</h1>
      <div class="year-nav">
        <button
          v-if="store.years.length"
          :disabled="!store.years.includes(yearParam - 1)"
          @click="goYear(yearParam - 1)"
        >
          <ChevronLeft :size="14" /> {{ yearParam - 1 }}年
        </button>
        <button
          v-if="store.years.length"
          :disabled="!store.years.includes(yearParam + 1)"
          @click="goYear(yearParam + 1)"
        >
          {{ yearParam + 1 }}年 <ChevronRight :size="14" />
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div class="loading" v-if="store.loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Question list -->
    <div class="exam-questions" v-if="!store.loading && store.items.length">
      <button
        v-for="(item, idx) in store.items"
        :key="item.id"
        class="exam-item"
        @click="viewQuestion(item.id)"
      >
        <span class="exam-item__num">{{ idx + 1 }}</span>
        <div class="exam-item__body">
          <p class="exam-item__text">{{ item.content.slice(0, 100) }}{{ item.content.length > 100 ? '...' : '' }}</p>
          <div class="exam-item__meta">
            <span class="exam-item__diff" :class="`d-${item.difficulty}`">
              {{ DIFFICULTY_LABELS[item.difficulty] || '中等' }}
            </span>
            <TopicTag
              v-for="tag in (item.knowledge_tags || []).slice(0, 2)"
              :key="tag"
              :label="tag"
            />
          </div>
        </div>
      </button>
    </div>

    <!-- Empty -->
    <div class="empty" v-if="!store.loading && !store.items.length">
      <FileText :size="40" class="empty-icon" />
      <p>该年份暂无真题数据</p>
      <button class="empty-btn" @click="router.push('/bank')">浏览其他年份</button>
    </div>
  </div>
</template>

<style scoped>
.exam-view {
  display: flex; flex-direction: column; gap: 1rem;
  padding-bottom: 3rem; max-width: 800px;
}

.back-btn {
  display: flex; align-items: center; gap: 0.4rem;
  background: none; border: none; color: #6b7280;
  font-size: 0.85rem; cursor: pointer; font-family: inherit;
  padding: 0; align-self: flex-start;
}

.year-bar {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 0.75rem;
}
.year-title {
  font-size: 1.5rem; font-weight: 800; color: #1f2937; margin: 0;
}
.year-nav {
  display: flex; gap: 0.5rem;
}
.year-nav button {
  display: flex; align-items: center; gap: 0.25rem;
  padding: 0.4rem 0.75rem; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08); background: white;
  font-size: 0.8rem; color: #374151; cursor: pointer; font-family: inherit;
  transition: all 0.15s;
}
.year-nav button:disabled { opacity: 0.3; cursor: not-allowed; }
.year-nav button:not(:disabled):hover { border-color: #8b5cf6; color: #8b5cf6; }

.exam-questions {
  display: flex; flex-direction: column; gap: 0.5rem;
}

.exam-item {
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1.25rem; border-radius: 14px;
  border: 1px solid rgba(0,0,0,0.06); background: white;
  text-align: left; cursor: pointer; transition: all 0.15s;
  font-family: inherit;
}
.exam-item:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  border-color: rgba(139,92,246,0.2);
}
.exam-item__num {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(135deg, #7c3aed, #8b5cf6);
  color: white; font-weight: 700; font-size: 0.85rem;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.exam-item__body { flex: 1; display: flex; flex-direction: column; gap: 0.5rem; }
.exam-item__text { font-size: 0.88rem; color: #374151; line-height: 1.6; margin: 0; }
.exam-item__meta { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.exam-item__diff {
  font-size: 0.7rem; font-weight: 600; padding: 0.1rem 0.4rem; border-radius: 6px;
}
.d-2 { background: #dcfce7; color: #16a34a; }
.d-3 { background: #fef3c7; color: #d97706; }
.d-4 { background: #fee2e2; color: #dc2626; }
.d-5 { background: #fce7f3; color: #db2777; }

.loading { text-align: center; padding: 3rem; color: #9ca3af; }
.loading-spinner {
  width: 32px; height: 32px; border: 3px solid #e5e7eb;
  border-top-color: #8b5cf6; border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 0.75rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

.empty { text-align: center; padding: 3rem; color: #9ca3af; }
.empty-icon { margin-bottom: 0.5rem; opacity: 0.4; }
.empty-btn {
  margin-top: 1rem; padding: 0.5rem 1.25rem; border-radius: 12px;
  border: none; background: linear-gradient(135deg, #7c3aed, #8b5cf6);
  color: white; font-size: 0.85rem; font-weight: 600; cursor: pointer; font-family: inherit;
}
</style>
