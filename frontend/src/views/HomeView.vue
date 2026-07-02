<script setup lang="ts">
/**
 * HomeView — 用户主页 Dashboard
 * 区别于 LandingView（外部营销入口）
 * 面向登录用户：展示学习数据、快速入口、推荐内容
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Camera,
  Code2,
  MessageCircle,
  Sparkles,
  Flame,
  Clock,
  TrendingUp,
  Target,
  BookOpen,
  ChevronRight,
  ArrowRight,
  Library,
  Network,
  Route,
  Brain,
  Trophy,
  Zap,
  Play,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useStudyTimerStore } from '@/stores/studyTimer'

const router = useRouter()
const auth = useAuthStore()
const timer = useStudyTimerStore()

const userName = computed(() => auth.user?.name || '同学')
const currentHour = new Date().getHours()
const greeting = computed(() => {
  if (currentHour < 6) return '夜深了'
  if (currentHour < 12) return '早上好'
  if (currentHour < 14) return '中午好'
  if (currentHour < 18) return '下午好'
  if (currentHour < 22) return '晚上好'
  return '夜深了'
})

// 滚动揭示
const visibleItems = ref<Set<string>>(new Set())
onMounted(() => {
  setTimeout(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const delay = parseInt(entry.target.getAttribute('data-reveal-delay') || '0')
            setTimeout(() => {
              entry.target.classList.add('is-revealed')
            }, delay)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -30px 0px' }
    )
    document.querySelectorAll('[data-reveal-id]').forEach((el) => observer.observe(el))
  }, 100)
})

// 核心数据
const stats = computed(() => [
  {
    key: 'today',
    label: '今日学习',
    value: timer.todayMinutes,
    unit: '分钟',
    icon: Clock,
    color: '#0d9488',
    bg: 'rgba(13, 148, 136, 0.08)',
  },
  {
    key: 'streak',
    label: '连续打卡',
    value: 7,
    unit: '天',
    icon: Flame,
    color: '#f59e0b',
    bg: 'rgba(245, 158, 11, 0.08)',
  },
  {
    key: 'total',
    label: '累计时长',
    value: 128,
    unit: '小时',
    icon: TrendingUp,
    color: '#3b82f6',
    bg: 'rgba(59, 130, 246, 0.08)',
  },
  {
    key: 'mastery',
    label: '整体掌握度',
    value: 78,
    unit: '%',
    icon: Target,
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.08)',
  },
])

// 快速入口
const quickEntries = [
  { key: 'camera', label: '拍照解题', desc: '上传题目', icon: Camera, path: '/camera' },
  { key: 'chat', label: 'AI 对话', desc: '苏格拉底', icon: MessageCircle, path: '/chat/ask' },
  { key: 'code', label: '代码实战', desc: '在线编程', icon: Code2, path: '/visualize' },
  { key: 'gen', label: '举一反三', desc: '智能出题', icon: Sparkles, path: '/problem-gen' },
  { key: 'path', label: '学习路径', desc: '规划路线', icon: Route, path: '/learning-path' },
  { key: 'book', label: '错题本', desc: '查漏补缺', icon: BookOpen, path: '/mistake-book' },
]

// 推荐题目（基于薄弱点）
const recommendedQuestions = [
  { id: '1', subject: '数据结构', tag: '二叉树遍历', difficulty: '中等', hot: true },
  { id: '2', subject: '操作系统', tag: '进程同步', difficulty: '困难', hot: false },
  { id: '3', subject: '计算机网络', tag: 'TCP 拥塞控制', difficulty: '中等', hot: false },
]

// 学习路径进度
const learningPaths = [
  { name: '数据结构', progress: 65, color: '#0d9488' },
  { name: '计算机网络', progress: 30, color: '#3b82f6' },
  { name: '操作系统', progress: 78, color: '#10b981' },
  { name: '计算机组成', progress: 42, color: '#8b5cf6' },
]

// 最近活动
const recentActivities = [
  { type: 'solve', text: '完成了「二叉树层序遍历」题目', time: '今天 14:32' },
  { type: 'mistake', text: '收录 1 道错题到错题本', time: '今天 11:15' },
  { type: 'path', text: '数据结构路径完成度 +5%', time: '昨天 22:08' },
]

function startLearning() {
  router.push('/chat/ask')
}
</script>

<template>
  <div class="home-dashboard">
    <!-- 欢迎区 -->
    <section
      class="welcome-section"
      data-reveal-id="welcome"
      data-reveal-delay="0"
    >
      <div class="welcome-bg" aria-hidden="true"></div>
      <div class="welcome-content">
        <div class="welcome-text">
          <p class="welcome-greeting">{{ greeting }}</p>
          <h1 class="welcome-name">{{ userName }}</h1>
          <p class="welcome-message">
            今日已学 <strong>{{ timer.todayMinutes }} 分钟</strong>，继续保持！
          </p>
        </div>
        <button
          class="welcome-cta"
          @click="startLearning"
        >
          <Play :size="16" />
          <span>开始学习</span>
        </button>
      </div>
    </section>

    <!-- 数据统计 4 列 -->
    <section
      class="stats-section"
      data-reveal-id="stats"
      data-reveal-delay="100"
    >
      <div
        v-for="(s, i) in stats"
        :key="s.key"
        class="stat-card"
        :data-reveal-id="`stat-${i}`"
        :data-reveal-delay="150 + i * 60"
      >
        <div class="stat-icon" :style="{ background: s.bg, color: s.color }">
          <component :is="s.icon" :size="18" />
        </div>
        <div class="stat-body">
          <div class="stat-value-row">
            <span class="stat-value">{{ s.value }}</span>
            <span class="stat-unit">{{ s.unit }}</span>
          </div>
          <p class="stat-label">{{ s.label }}</p>
        </div>
      </div>
    </section>

    <!-- 快速入口 6 宫格 -->
    <section
      class="entries-section"
      data-reveal-id="entries"
      data-reveal-delay="300"
    >
      <div class="section-header">
        <h2 class="section-title">快速入口</h2>
        <span class="section-subtitle">6 种学习方式</span>
      </div>
      <div class="entries-grid">
        <button
          v-for="(e, i) in quickEntries"
          :key="e.key"
          class="entry-card"
          :data-reveal-id="`entry-${i}`"
          :data-reveal-delay="350 + i * 50"
          @click="router.push(e.path)"
        >
          <div class="entry-icon">
            <component :is="e.icon" :size="22" />
          </div>
          <p class="entry-label">{{ e.label }}</p>
          <p class="entry-desc">{{ e.desc }}</p>
        </button>
      </div>
    </section>

    <!-- 双列：推荐 + 学习路径 -->
    <div class="dual-section">
      <!-- 推荐题目 -->
      <section
        class="card-block"
        data-reveal-id="reco"
        data-reveal-delay="600"
      >
        <div class="section-header">
          <h2 class="section-title">
            <Sparkles :size="16" class="section-icon" />
            <span>为你推荐</span>
          </h2>
          <a class="section-link" @click="router.push('/bank')">
            <span>查看更多</span>
            <ChevronRight :size="14" />
          </a>
        </div>
        <ul class="reco-list">
          <li
            v-for="(q, i) in recommendedQuestions"
            :key="q.id"
            class="reco-item"
            :data-reveal-id="`reco-${i}`"
            :data-reveal-delay="650 + i * 60"
            @click="router.push('/chat/ask')"
          >
            <span class="reco-tag" :class="`tag-${q.subject.length}`">{{ q.subject }}</span>
            <span class="reco-title">{{ q.tag }}</span>
            <span class="reco-difficulty" :class="`diff-${q.difficulty}`">{{ q.difficulty }}</span>
            <ArrowRight :size="14" class="reco-arrow" />
          </li>
        </ul>
      </section>

      <!-- 学习路径 -->
      <section
        class="card-block"
        data-reveal-id="path"
        data-reveal-delay="700"
      >
        <div class="section-header">
          <h2 class="section-title">
            <Route :size="16" class="section-icon" />
            <span>学习路径</span>
          </h2>
          <a class="section-link" @click="router.push('/learning-path')">
            <span>详情</span>
            <ChevronRight :size="14" />
          </a>
        </div>
        <ul class="path-list">
          <li
            v-for="(p, i) in learningPaths"
            :key="p.name"
            class="path-item"
            :data-reveal-id="`path-${i}`"
            :data-reveal-delay="750 + i * 60"
          >
            <div class="path-row">
              <span class="path-name">{{ p.name }}</span>
              <span class="path-percent" :style="{ color: p.color }">{{ p.progress }}%</span>
            </div>
            <div class="path-track">
              <div
                class="path-fill"
                :style="{ width: p.progress + '%', background: p.color }"
              ></div>
            </div>
          </li>
        </ul>
      </section>
    </div>

    <!-- 最近活动 -->
    <section
      class="activity-section"
      data-reveal-id="activity"
      data-reveal-delay="800"
    >
      <div class="section-header">
        <h2 class="section-title">
          <Trophy :size="16" class="section-icon" />
          <span>最近活动</span>
        </h2>
      </div>
      <ul class="activity-list">
        <li
          v-for="(a, i) in recentActivities"
          :key="i"
          class="activity-item"
          :data-reveal-id="`act-${i}`"
          :data-reveal-delay="850 + i * 50"
        >
          <div class="activity-dot"></div>
          <div class="activity-content">
            <p class="activity-text">{{ a.text }}</p>
            <p class="activity-time">{{ a.time }}</p>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
/* ============================================
   HOME DASHBOARD — 大气简约
   ============================================ */

.home-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* ===== Reveal Animations ===== */
[data-reveal-id] {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}
[data-reveal-id].is-revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ===== 欢迎区 ===== */
.welcome-section {
  position: relative;
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 16px;
  padding: 1.5rem 1.75rem;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.welcome-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 60% 80% at 100% 50%, rgba(13, 148, 136, 0.06) 0%, transparent 60%);
  pointer-events: none;
}

.welcome-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.welcome-text {
  flex: 1;
  min-width: 0;
}

.welcome-greeting {
  font-size: 0.8125rem;
  color: #94a3b8;
  font-weight: 500;
  margin: 0 0 0.25rem;
  letter-spacing: 0.02em;
}

.welcome-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 0.375rem;
  letter-spacing: -0.02em;
}

.welcome-message {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.welcome-message strong {
  color: #0d9488;
  font-weight: 600;
  font-feature-settings: "tnum";
}

.welcome-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #0d9488;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.875rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25);
  flex-shrink: 0;
}

.welcome-cta:hover {
  background: #0f766e;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(13, 148, 136, 0.35);
}

.welcome-cta:active {
  transform: scale(0.98);
}

/* ===== 统计卡 4 列 ===== */
.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
}

@media (max-width: 768px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 12px;
  padding: 1rem 1.125rem;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: rgba(15, 23, 42, 0.1);
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.06);
  transform: translateY(-1px);
}

.stat-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  margin-bottom: 2px;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.02em;
  line-height: 1;
  font-feature-settings: "tnum";
}

.stat-unit {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  margin: 0;
  letter-spacing: 0.01em;
}

/* ===== Section 通用 ===== */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.875rem;
  padding: 0 0.125rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0;
  letter-spacing: -0.005em;
}

.section-icon {
  color: #0d9488;
}

.section-subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
  font-weight: 500;
}

.section-link {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s ease;
}

.section-link:hover {
  color: #0d9488;
}

/* ===== 快速入口 6 宫格 ===== */
.entries-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.625rem;
}

@media (max-width: 1024px) {
  .entries-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 640px) {
  .entries-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }
}

.entry-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0.5rem;
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.entry-card:hover {
  border-color: rgba(13, 148, 136, 0.2);
  background: rgba(13, 148, 136, 0.02);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px -6px rgba(13, 148, 136, 0.15);
}

.entry-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(13, 148, 136, 0.08);
  color: #0d9488;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 0.5rem;
  transition: all 0.2s ease;
}

.entry-card:hover .entry-icon {
  background: #0d9488;
  color: white;
  transform: scale(1.05);
}

.entry-label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 2px;
  line-height: 1.2;
}

.entry-desc {
  font-size: 0.6875rem;
  color: #94a3b8;
  margin: 0;
  line-height: 1.2;
}

/* ===== 双列布局 ===== */
.dual-section {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 1rem;
}

@media (max-width: 1024px) {
  .dual-section {
    grid-template-columns: 1fr;
  }
}

.card-block {
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 14px;
  padding: 1.25rem 1.375rem;
}

/* ===== 推荐列表 ===== */
.reco-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reco-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  background: #f8fafc;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.8125rem;
}

.reco-item:hover {
  background: rgba(13, 148, 136, 0.05);
  transform: translateX(2px);
}

.reco-tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
  border-radius: 4px;
  font-size: 0.6875rem;
  font-weight: 500;
  flex-shrink: 0;
}

.reco-title {
  flex: 1;
  color: #0f172a;
  font-weight: 500;
}

.reco-difficulty {
  font-size: 0.6875rem;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

.diff-中等 { background: rgba(245, 158, 11, 0.1); color: #d97706; }
.diff-困难 { background: rgba(239, 68, 68, 0.1); color: #dc2626; }
.diff-简单 { background: rgba(16, 185, 129, 0.1); color: #059669; }

.reco-arrow {
  color: #94a3b8;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.reco-item:hover .reco-arrow {
  color: #0d9488;
  transform: translateX(2px);
}

/* ===== 路径列表 ===== */
.path-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.path-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.path-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.path-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #0f172a;
}

.path-percent {
  font-size: 0.875rem;
  font-weight: 700;
  font-feature-settings: "tnum";
  letter-spacing: -0.01em;
}

.path-track {
  height: 6px;
  background: #f1f5f9;
  border-radius: 999px;
  overflow: hidden;
}

.path-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

/* ===== 活动时间线 ===== */
.activity-section {
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 14px;
  padding: 1.25rem 1.375rem;
}

.activity-list {
  list-style: none;
  margin: 0;
  padding: 0;
  position: relative;
}

.activity-list::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  background: #e2e8f0;
}

.activity-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.625rem 0;
  position: relative;
}

.activity-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: #0d9488;
  flex-shrink: 0;
  margin-top: 4px;
  position: relative;
  z-index: 1;
  box-shadow: 0 0 0 3px white;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-text {
  font-size: 0.8125rem;
  color: #0f172a;
  margin: 0 0 2px;
  font-weight: 500;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.6875rem;
  color: #94a3b8;
  margin: 0;
}

/* ===== 响应式 ===== */
@media (max-width: 640px) {
  .welcome-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }

  .welcome-cta {
    align-self: flex-start;
  }

  .welcome-name {
    font-size: 1.25rem;
  }
}
</style>
