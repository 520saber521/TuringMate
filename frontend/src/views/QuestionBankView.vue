<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useQuestionBankStore } from '@/stores/questionBank'
import { Library, FileText, Search, TrendingUp, BookMarked, ArrowRight } from 'lucide-vue-next'

const router = useRouter()
const store = useQuestionBankStore()
const searchKeyword = ref('')

const subjectCards = [
  { id: '数据结构', name: '数据结构', icon: '🌳', color: '#7c3aed', bg: 'rgba(124,58,237,0.08)', count: 0 },
  { id: '计组', name: '计算机组成原理', icon: '💻', color: '#0ea5e9', bg: 'rgba(14,165,233,0.08)', count: 0 },
  { id: '操作系统', name: '操作系统', icon: '⚙️', color: '#f59e0b', bg: 'rgba(245,158,11,0.08)', count: 0 },
  { id: '计算机网络', name: '计算机网络', icon: '🌐', color: '#10b981', bg: 'rgba(16,185,129,0.08)', count: 0 },
]

onMounted(() => {
  store.fetchYears()
  store.fetchSubjects()
})

function goToList(subject?: string, tag?: string) {
  const query: Record<string, string> = {}
  if (subject) query.subject = subject
  if (tag) query.tag = tag
  router.push({ path: '/bank/list', query })
}

function goToExam(year: number) {
  router.push(`/bank/exam/${year}`)
}

function onSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/bank/list', query: { keyword: searchKeyword.value.trim() } })
  }
}
</script>

<template>
  <div class="bank-home">
    <!-- Hero Section -->
    <section class="hero">
      <h1 class="hero__title">408 考研题库</h1>
      <p class="hero__subtitle">历年真题 + 章节练习 + AI 智能解析，助你高效备考</p>
      <div class="hero__search">
        <div class="search-box">
          <Search :size="18" class="search-box__icon" />
          <input
            v-model="searchKeyword"
            type="text"
            class="search-box__input"
            placeholder="搜索题目、知识点..."
            @keyup.enter="onSearch"
          />
          <button class="search-box__btn" @click="onSearch">搜索</button>
        </div>
      </div>
    </section>

    <!-- Subject Cards -->
    <section class="subjects">
      <div class="section-header">
        <h2 class="section-title">按科目练习</h2>
      </div>
      <div class="subject-grid">
        <button
          v-for="card in subjectCards"
          :key="card.id"
          class="subject-card"
          :style="{ '--card-color': card.color, '--card-bg': card.bg }"
          @click="goToList(card.id)"
        >
          <span class="subject-card__icon">{{ card.icon }}</span>
          <div class="subject-card__info">
            <span class="subject-card__name">{{ card.name }}</span>
            <span class="subject-card__action">
              开始练习 <ArrowRight :size="14" />
            </span>
          </div>
        </button>
      </div>
    </section>

    <!-- Year Timeline -->
    <section class="years" v-if="store.years.length">
      <div class="section-header">
        <h2 class="section-title">历年真题</h2>
        <button class="section-link" @click="goToList()">
          全部题目 <ArrowRight :size="14" />
        </button>
      </div>
      <div class="year-timeline">
        <button
          v-for="year in store.years"
          :key="year"
          class="year-chip"
          @click="goToExam(year)"
        >
          <FileText :size="14" />
          <span>{{ year }}年真题</span>
        </button>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="actions">
      <div class="action-card" @click="router.push('/mistake-book')">
        <BookMarked :size="24" class="action-card__icon" style="color: #ef4444;" />
        <div class="action-card__text">
          <span class="action-card__title">我的错题本</span>
          <span class="action-card__desc">查看收集的错题，针对复习</span>
        </div>
        <ArrowRight :size="14" class="action-card__arrow" />
      </div>
      <div class="action-card" @click="goToList()">
        <TrendingUp :size="24" class="action-card__icon" style="color: #7c3aed;" />
        <div class="action-card__text">
          <span class="action-card__title">智能推荐</span>
          <span class="action-card__desc">根据薄弱点推送练习题目</span>
        </div>
        <ArrowRight :size="14" class="action-card__arrow" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.bank-home {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  padding-bottom: 3rem;
}

/* Hero */
.hero {
  text-align: center;
  padding: 2.5rem 1rem 1.5rem;
}
.hero__title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hero__subtitle {
  margin-top: 0.5rem;
  color: #9ca3af;
  font-size: 0.95rem;
}
.hero__search {
  margin-top: 1.5rem;
  display: flex;
  justify-content: center;
}
.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 16px;
  padding: 0.4rem 0.4rem 0.4rem 1rem;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 4px 24px rgba(139, 92, 246, 0.08);
  transition: box-shadow 0.2s;
}
.search-box:focus-within {
  box-shadow: 0 4px 24px rgba(139, 92, 246, 0.18);
  border-color: rgba(139, 92, 246, 0.3);
}
.search-box__icon { color: #9ca3af; flex-shrink: 0; }
.search-box__input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 0.9rem;
  font-family: inherit;
  color: #1f2937;
  background: transparent;
}
.search-box__input::placeholder { color: #cbd5e1; }
.search-box__btn {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #7c3aed, #8b5cf6);
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.search-box__btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(124,58,237,0.3); }

/* Sections */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: #1f2937;
}
.section-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: #8b5cf6;
  font-size: 0.85rem;
  cursor: pointer;
  font-family: inherit;
}

/* Subject Grid */
.subject-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
@media (min-width: 768px) {
  .subject-grid { grid-template-columns: repeat(4, 1fr); }
}
.subject-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.06);
  background: var(--card-bg, white);
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
}
.subject-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}
.subject-card__icon { font-size: 1.75rem; }
.subject-card__info { display: flex; flex-direction: column; gap: 0.2rem; text-align: left; }
.subject-card__name { font-weight: 600; color: #1f2937; font-size: 0.9rem; }
.subject-card__action { display: flex; align-items: center; gap: 0.2rem; color: var(--card-color); font-size: 0.78rem; font-weight: 500; }

/* Year Timeline */
.year-timeline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.year-chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(0,0,0,0.08);
  background: white;
  color: #374151;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}
.year-chip:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
  background: rgba(139,92,246,0.04);
}

/* Action Cards */
.actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.action-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,0.06);
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}
.action-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.04);
  transform: translateX(4px);
}
.action-card__icon { flex-shrink: 0; }
.action-card__text { flex: 1; display: flex; flex-direction: column; gap: 0.15rem; text-align: left; }
.action-card__title { font-weight: 600; color: #1f2937; font-size: 0.9rem; }
.action-card__desc { font-size: 0.8rem; color: #9ca3af; }
.action-card__arrow { color: #cbd5e1; }
</style>
