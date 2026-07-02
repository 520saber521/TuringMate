<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useQuestionBankStore } from '@/stores/questionBank'
import { useAuthStore } from '@/stores/auth'
import { ArrowLeft, Bookmark, BookmarkCheck, Share2, AlertCircle } from 'lucide-vue-next'
import AIAnalysisPanel from '@/components/question/AIAnalysisPanel.vue'
import TopicTag from '@/components/question/TopicTag.vue'
import apiClient from '@/api/index'

const route = useRoute()
const router = useRouter()
const store = useQuestionBankStore()
const auth = useAuthStore()

const questionId = route.params.questionId as string
const addingMistake = ref(false)
const mistakeAdded = ref(false)
const mistakeError = ref('')

const DIFFICULTY_LABELS: Record<number, string> = {
  1: '基础', 2: '简单', 3: '中等', 4: '较难', 5: '困难',
}

const DIFFICULTY_COLORS: Record<number, string> = {
  1: '#22c55e', 2: '#84cc16', 3: '#f59e0b', 4: '#f97316', 5: '#ef4444',
}

onMounted(() => {
  store.fetchQuestionDetail(questionId)
})

async function addToMistakeBook() {
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }
  if (mistakeAdded.value) return
  addingMistake.value = true
  mistakeError.value = ''
  try {
    await apiClient.post('/mistakes', {
      question_id: questionId,
      knowledge_tags: store.currentQuestion?.knowledge_tags || [],
    })
    mistakeAdded.value = true
  } catch (e: any) {
    if (e?.response?.data?.message?.includes('已存在')) {
      mistakeAdded.value = true
    } else {
      mistakeError.value = e?.userMessage || '添加失败，请重试'
    }
  } finally {
    addingMistake.value = false
  }
}
</script>

<template>
  <div class="solve-view">
    <!-- Back button -->
    <button class="back-btn" @click="router.back()">
      <ArrowLeft :size="16" /> 返回
    </button>

    <!-- Loading -->
    <div class="loading" v-if="store.questionLoading">
      <div class="loading-spinner"></div>
      <p>加载题目中...</p>
    </div>

    <!-- Question Content -->
    <template v-if="store.currentQuestion && !store.questionLoading">
      <div class="question-card">
        <!-- Meta -->
        <div class="question-meta">
          <div class="meta-left">
            <span class="subject-tag">{{ store.currentQuestion.subject }}</span>
            <span
              class="diff-tag"
              :style="{ background: `${DIFFICULTY_COLORS[store.currentQuestion.difficulty]}15`, color: DIFFICULTY_COLORS[store.currentQuestion.difficulty] }"
            >
              {{ DIFFICULTY_LABELS[store.currentQuestion.difficulty] || '中等' }}
            </span>
            <span class="year-tag" v-if="store.currentQuestion.year">{{ store.currentQuestion.year }}年</span>
          </div>
          <div class="meta-right">
            <span class="exam-tag" v-if="store.currentQuestion.exam_paper">{{ store.currentQuestion.exam_paper }}</span>
          </div>
        </div>

        <!-- Title / Content -->
        <div class="question-content">
          <p>{{ store.currentQuestion.content }}</p>
        </div>

        <!-- Image if any -->
        <div class="question-image" v-if="store.currentQuestion.image_url">
          <img :src="store.currentQuestion.image_url" alt="题目图片" />
        </div>

        <!-- Knowledge Tags -->
        <div class="question-tags" v-if="store.currentQuestion.knowledge_tags?.length">
          <TopicTag
            v-for="tag in store.currentQuestion.knowledge_tags"
            :key="tag"
            :label="tag"
          />
        </div>

        <!-- Action bar -->
        <div class="question-actions">
          <button
            class="action-btn"
            :class="{ active: mistakeAdded }"
            :disabled="addingMistake || mistakeAdded"
            @click="addToMistakeBook"
          >
            <component :is="mistakeAdded ? BookmarkCheck : Bookmark" :size="16" />
            <span>{{ mistakeAdded ? '已收藏' : addingMistake ? '添加中...' : '加入错题本' }}</span>
          </button>
          <p class="mistake-error" v-if="mistakeError">{{ mistakeError }}</p>
          <button class="action-btn" disabled>
            <Share2 :size="16" />
            <span>分享</span>
          </button>
        </div>
      </div>

      <!-- AI Analysis Panel -->
      <AIAnalysisPanel
        :solution-steps="store.currentQuestion.solution_steps || []"
        :ai-analysis="store.currentQuestion.ai_analysis"
        :question-content="store.currentQuestion.content"
      />
    </template>

    <!-- Not Found -->
    <div class="not-found" v-if="store.questionError && !store.questionLoading">
      <AlertCircle :size="32" class="text-slate-300" />
      <p>{{ store.questionError }}</p>
      <button class="back-link" @click="router.push('/bank')">返回题库</button>
    </div>
  </div>
</template>

<style scoped>
.solve-view {
  display: flex; flex-direction: column; gap: 1rem;
  padding-bottom: 3rem; max-width: 800px;
}

.back-btn {
  display: flex; align-items: center; gap: 0.4rem;
  background: none; border: none; color: #6b7280;
  font-size: 0.85rem; cursor: pointer; font-family: inherit;
  padding: 0; align-self: flex-start;
}
.back-btn:hover { color: #1f2937; }

/* Question Card */
.question-card {
  padding: 1.5rem; border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.06); background: white;
  display: flex; flex-direction: column; gap: 1rem;
}
.question-meta {
  display: flex; align-items: center; justify-content: space-between;
  flex-wrap: wrap; gap: 0.5rem;
}
.meta-left, .meta-right { display: flex; align-items: center; gap: 0.4rem; }
.subject-tag {
  font-size: 0.75rem; font-weight: 700; padding: 0.2rem 0.6rem;
  border-radius: 8px; background: rgba(139,92,246,0.1); color: #7c3aed;
}
.diff-tag {
  font-size: 0.72rem; font-weight: 600; padding: 0.2rem 0.5rem; border-radius: 6px;
}
.year-tag {
  font-size: 0.72rem; padding: 0.2rem 0.5rem;
  border-radius: 6px; background: #f1f5f9; color: #64748b;
}
.exam-tag {
  font-size: 0.72rem; color: #9ca3af;
}

.question-content {
  font-size: 0.95rem; color: #1f2937; line-height: 1.8;
}
.question-content p { margin: 0; }

.question-image img {
  max-width: 100%; border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);
}

.question-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }

.question-actions {
  display: flex; align-items: center; gap: 0.75rem;
  padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.04);
}
.action-btn {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.45rem 0.85rem; border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08); background: white;
  color: #6b7280; font-size: 0.82rem;
  cursor: pointer; font-family: inherit; transition: all 0.15s;
}
.action-btn:hover:not(:disabled) { border-color: #8b5cf6; color: #8b5cf6; }
.action-btn.active { border-color: #10b981; color: #10b981; background: rgba(16,185,129,0.06); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.mistake-error { font-size: 0.75rem; color: #ef4444; margin: 0; }

/* Loading */
.loading { text-align: center; padding: 4rem; color: #9ca3af; }
.loading-spinner {
  width: 32px; height: 32px; border: 3px solid #e5e7eb;
  border-top-color: #8b5cf6; border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin: 0 auto 0.75rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Not Found */
.not-found { text-align: center; padding: 4rem; color: #9ca3af; }
.back-link {
  display: inline-block; margin-top: 1rem;
  color: #8b5cf6; cursor: pointer; font-weight: 500;
}
</style>
