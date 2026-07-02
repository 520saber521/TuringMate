<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, BookOpen, Trash2, RotateCcw, CheckCircle2, Search, Filter } from 'lucide-vue-next'
import { useMistakeBookStore } from '@/stores/mistakeBook'
import type { Mistake } from '@/stores/mistakeBook'

const router = useRouter()
const store = useMistakeBookStore()

const SUBJECTS = ['全部', '数据结构', '计组', '操作系统', '网络']
const STATUS_FILTERS = ['全部', '待复习', '已掌握'] as const

const activeSubject = ref('全部')
const activeStatus = ref('全部')

const filteredMistakes = computed(() => {
  let list = [...store.mistakes]
  if (activeSubject.value !== '全部') {
    list = list.filter(m => m.subject === activeSubject.value)
  }
  if (activeStatus.value === '待复习') {
    list = list.filter(m => !m.reviewed)
  } else if (activeStatus.value === '已掌握') {
    list = list.filter(m => m.reviewed)
  }
  return list
})

function goToReview(mistake: Mistake) {
  const questionId = mistake.questionId || mistake.id
  router.push({ path: `/chat/${questionId}`, query: { subject: mistake.subject } })
}

function formatDate(ts: number): string {
  const d = new Date(ts)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 86400000) return '今天'
  if (diff < 172800000) return '昨天'
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

const emptyMessage = computed(() => {
  if (store.totalCount === 0) return { title: '还没有错题', desc: '在 AI 对话中发现错题时，点击"加入错题本"即可收录到这里' }
  if (activeSubject.value !== '全部') return { title: `没有${activeSubject.value}的错题`, desc: '试试切换其他科目筛选' }
  return { title: '没有符合条件的错题', desc: '试试切换筛选条件' }
})
</script>

<template>
  <div class="mistake-view animate-fade-in-up pb-6">
    <!-- Header -->
    <header class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-amber-50 flex items-center justify-center transition-colors"
        @click="router.back()">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">错题本</h2>
    </header>

    <!-- Warm intro -->
    <div class="mb-intro mb-5">
      <p class="mb-intro__overline font-serif">错题收集 · 针对性复习</p>
      <h1 class="mb-intro__title">每个错误，都是通往满分的阶梯</h1>
    </div>

    <!-- Stats bar -->
    <div class="mb-stats flex items-center gap-4 mb-5">
      <div class="mb-stat">
        <span class="mb-stat__num">{{ store.totalCount }}</span>
        <span class="mb-stat__lbl">总计</span>
      </div>
      <div class="mb-stat-divider"></div>
      <div class="mb-stat mb-stat--review">
        <span class="mb-stat__num">{{ store.unreviewedCount }}</span>
        <span class="mb-stat__lbl">待复习</span>
      </div>
      <div class="mb-stat-divider"></div>
      <div class="mb-stat mb-stat--done">
        <span class="mb-stat__num">{{ store.reviewedCount }}</span>
        <span class="mb-stat__lbl">已掌握</span>
      </div>
    </div>

    <!-- Filter bar -->
    <div class="mb-filters flex flex-col gap-2 mb-5">
      <!-- Subject tabs -->
      <div class="mb-filter-row flex items-center gap-1.5 flex-wrap">
        <Filter :size="13" class="text-text-muted mr-0.5" />
        <button
          v-for="s in SUBJECTS"
          :key="s"
          :class="['mb-filter-chip', { active: activeSubject === s }]"
          @click="activeSubject = s"
        >{{ s }}</button>
      </div>
      <!-- Status tabs -->
      <div class="mb-filter-row flex items-center gap-1.5">
        <span class="text-[11px] text-text-muted mr-1">{{ store.unreviewedCount }}道待复习</span>
        <button
          v-for="st in STATUS_FILTERS"
          :key="st"
          :class="['mb-filter-chip mb-filter-chip--sm', { active: activeStatus === st }]"
          @click="activeStatus = st"
        >{{ st }}</button>
      </div>
    </div>

    <!-- Mistake list -->
    <div v-if="filteredMistakes.length > 0" class="space-y-3">
      <div
        v-for="m in filteredMistakes"
        :key="m.id"
        :class="['mistake-card rounded-2xl p-4', { reviewed: m.reviewed }]"
      >
        <!-- Top: content + actions -->
        <div class="flex items-start justify-between gap-3 mb-2">
          <p class="mistake-card__content text-sm font-medium text-truncate-2 flex-1">{{ m.questionContent }}</p>
          <div class="flex items-center gap-1 flex-shrink-0">
            <button
              class="mistake-card__action"
              :title="m.reviewed ? '标记为待复习' : '标记为已掌握'"
              @click.stop="m.reviewed ? store.markUnreviewed(m.id) : store.markReviewed(m.id)"
            >
              <CheckCircle2 v-if="m.reviewed" :size="16" class="text-success-500" />
              <RotateCcw v-else :size="16" />
            </button>
            <button class="mistake-card__action mistake-card__action--danger" title="删除"
              @click.stop="store.removeMistake(m.id)">
              <Trash2 :size="15" />
            </button>
          </div>
        </div>

        <!-- Tags row -->
        <div class="flex items-center gap-1.5 flex-wrap mb-2">
          <span class="mistake-card__subj">{{ m.subject }}</span>
          <span class="mistake-card__error-tag">{{ m.errorReason }}</span>
          <span
            v-for="tag in m.knowledgeTags.slice(0, 2)"
            :key="tag"
            class="mistake-card__k-tag"
          >{{ tag }}</span>
        </div>

        <!-- Bottom: date + review button -->
        <div class="flex items-center justify-between">
          <span class="text-[11px] text-text-muted">{{ formatDate(m.addedAt) }}</span>
          <button class="mistake-card__review-btn" @click="goToReview(m)">
            去复习 →
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else class="empty-stage text-center py-16">
      <div class="empty-stage__icon mb-4">
        <BookOpen :size="44" />
      </div>
      <p class="font-semibold text-base mb-1" style="color: var(--color-text-secondary)">{{ emptyMessage.title }}</p>
      <p class="text-sm" style="color: var(--color-text-tertiary)">{{ emptyMessage.desc }}</p>
    </div>
  </div>
</template>

<style scoped>
.mistake-view { max-width: 800px; margin: 0 auto; padding: 1.5rem; }

/* Intro */
.mb-intro { text-align: center; }
.mb-intro__overline {
  font-size: 0.88rem;
  color: var(--color-amber-600);
  letter-spacing: 0.04em;
  margin-bottom: 0.3rem;
}
.mb-intro__title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
}

/* Stats */
.mb-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  background: var(--surface-paper-bg);
  border: 1px solid var(--surface-paper-border);
  border-radius: var(--radius-xl);
}
.mb-stat { display: flex; flex-direction: column; align-items: center; gap: 0.1rem; min-width: 64px; }
.mb-stat__num { font-size: 1.4rem; font-weight: 800; color: var(--color-text-primary); line-height: 1; }
.mb-stat__lbl { font-size: 0.68rem; color: var(--color-text-muted); }
.mb-stat--review .mb-stat__num { color: var(--color-amber-500); }
.mb-stat--done .mb-stat__num { color: var(--color-success-500); }
.mb-stat-divider { width: 1px; height: 28px; background: var(--color-border-light); }

/* Filters */
.mb-filter-row { }
.mb-filter-chip {
  padding: 0.25rem 0.7rem;
  border-radius: 999px;
  border: 1px solid var(--color-border-light);
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.75rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s ease;
}
.mb-filter-chip:hover { border-color: var(--color-border); color: var(--color-text-primary); }
.mb-filter-chip.active {
  background: rgba(124, 58, 237, 0.08);
  border-color: var(--color-primary-300);
  color: var(--color-primary-600);
  font-weight: 600;
}
.mb-filter-chip--sm { font-size: 0.7rem; padding: 0.2rem 0.55rem; }

/* Mistake card */
.mistake-card {
  background: var(--surface-paper-bg);
  border: 1px solid var(--surface-paper-border);
  transition: all 0.2s ease;
}
.mistake-card:hover { box-shadow: var(--shadow-sm); }
.mistake-card.reviewed { opacity: 0.55; }
.mistake-card__content {
  color: var(--color-text-primary);
  line-height: 1.5;
}
.mistake-card__action {
  width: 30px; height: 30px;
  border-radius: 8px; border: none;
  background: transparent;
  color: var(--color-text-muted);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s ease;
}
.mistake-card__action:hover { background: var(--color-bg-secondary); color: var(--color-text-primary); }
.mistake-card__action--danger:hover { background: rgba(239, 68, 68, 0.08); color: #ef4444; }

.mistake-card__subj {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: rgba(124, 58, 237, 0.08);
  color: var(--color-primary-600);
}
.mistake-card__error-tag {
  font-size: 0.68rem;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  font-weight: 500;
}
.mistake-card__k-tag {
  font-size: 0.65rem;
  padding: 0.12rem 0.45rem;
  border-radius: 999px;
  background: var(--color-bg-secondary);
  color: var(--color-text-tertiary);
}
.mistake-card__review-btn {
  background: none; border: none;
  font-family: inherit; font-size: 0.78rem;
  font-weight: 600; cursor: pointer;
  color: var(--color-primary-500);
  transition: all 0.15s ease;
}
.mistake-card__review-btn:hover { color: var(--color-primary-700); }

/* Empty */
.empty-stage__icon { color: var(--color-text-muted); opacity: 0.25; }
</style>
