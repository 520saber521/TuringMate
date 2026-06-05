<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Camera,
  PenTool,
  Code2,
  MessageSquareText,
  ArrowRight,
  Sparkles,
  Brain,
  Eye,
  Users,
  Zap,
  ChevronRight,
  Lightbulb,
  Repeat,
  Heart,
  BarChart3,
  Play,
  TrendingUp,
  Star,
  Binary,
  Cpu,
  Monitor,
  Globe,
  Quote,
} from 'lucide-vue-next'

const router = useRouter()

const searchQuery = ref('')
const searchFocused = ref(false)

function handleSearch() {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push({ path: '/chat/ask', query: { q } })
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter') handleSearch()
}

const askMethods = [
  {
    key: 'photo',
    label: '拍照搜题',
    desc: '一拍即答',
    icon: Camera,
    path: '/photo-search',
    gradient: 'from-sky-400 via-blue-500 to-indigo-500',
    shadowColor: 'rgba(56,189,248,0.3)',
  },
  {
    key: 'handwrite',
    label: '手写批改',
    desc: 'AI 点评',
    icon: PenTool,
    path: '/correction',
    gradient: 'from-emerald-400 via-green-500 to-teal-500',
    shadowColor: 'rgba(52,211,153,0.3)',
  },
  {
    key: 'code',
    label: '代码实战',
    desc: '在线编码',
    icon: Code2,
    path: '/visualize',
    gradient: 'from-rose-400 via-pink-500 to-fuchsia-500',
    shadowColor: 'rgba(244,114,182,0.3)',
  },
  {
    key: 'text',
    label: '文字提问',
    desc: '苏格拉底',
    icon: MessageSquareText,
    path: '/chat/demo',
    gradient: 'from-amber-400 via-orange-500 to-red-500',
    shadowColor: 'rgba(251,191,36,0.3)',
  },
]

const subjects = [
  { name: '数据结构', icon: Binary, color: '#7c3aed', bg: 'rgba(99,102,241,0.08)', count: 128, hot: true, progress: 65 },
  { name: '计组', icon: Cpu, color: '#0EA5E9', bg: 'rgba(14,165,233,0.08)', count: 96, hot: false, progress: 42 },
  { name: '操作系统', icon: Monitor, color: '#10B981', bg: 'rgba(16,185,129,0.08)', count: 84, hot: true, progress: 78 },
  { name: '网络', icon: Globe, color: '#F43F5E', bg: 'rgba(244,63,94,0.08)', count: 72, hot: false, progress: 30 },
]

function goToSubject(subjectName: string) {
  searchQuery.value = `[${subjectName}] `
  const el = document.getElementById('main-search-input')
  el?.focus()
}

const recentQuestions = [
  {
    id: '1',
    question: '快速排序的时间复杂度为什么最坏是 O(n²)？',
    subject: '数据结构',
    accent: 'from-indigo-500 to-violet-500',
    accentColor: '#7c3aed',
    time: '10分钟前',
    replies: 3,
  },
  {
    id: '2',
    question: '进程和线程的本质区别是什么？',
    subject: '操作系统',
    accent: 'from-emerald-500 to-teal-500',
    accentColor: '#10B981',
    time: '1小时前',
    replies: 5,
  },
  {
    id: '3',
    question: '流水线的数据冒险怎么解决？',
    subject: '计组',
    accent: 'from-sky-500 to-blue-500',
    accentColor: '#0EA5E9',
    time: '3小时前',
    replies: 0,
  },
  {
    id: '4',
    question: 'TCP 三次握手为什么不是两次？',
    subject: '网络',
    accent: 'from-rose-500 to-red-500',
    accentColor: '#F43F5E',
    time: '昨天',
    replies: 8,
  },
]

function openQuestion(qId: string) {
  router.push(`/chat/${qId}`)
}

const aiPowers = [
  {
    title: '苏格拉底引导',
    desc: '不给答案，引导你自己想通',
    icon: Brain,
    color: '#7c3aed',
    gradient: 'from-indigo-500 via-violet-500 to-purple-500',
    size: 'large' as const,
    path: '/chat/demo',
  },
  {
    title: '举一反三',
    desc: '一道题变出N道变体',
    icon: Repeat,
    color: '#0EA5E9',
    gradient: 'from-cyan-500 via-sky-500 to-blue-500',
    size: 'small' as const,
    path: '/chat/demo',
  },
  {
    title: '思维回放',
    desc: '可视化你的解题思考链路',
    icon: Eye,
    color: '#a78bfa',
    gradient: 'from-violet-500 via-purple-500 to-fuchsia-500',
    size: 'small' as const,
    path: '/diagnosis',
  },
  {
    title: 'AI 研友',
    desc: '虚拟学习伙伴陪你讨论',
    icon: Users,
    color: '#10B981',
    gradient: 'from-emerald-500 via-green-500 to-teal-500',
    size: 'small' as const,
    path: '/chat/demo',
  },
  {
    title: '情绪感知',
    desc: '懂你心情的智能导师',
    icon: Heart,
    color: '#EC4899',
    gradient: 'from-pink-500 via-rose-500 to-red-500',
    size: 'small' as const,
    path: '/chat/demo',
  },
  {
    title: '代码实战',
    desc: '在线编码 + AI 评审 + 实时运行',
    icon: Code2,
    color: '#F59E0B',
    gradient: 'from-amber-500 via-orange-500 to-yellow-500',
    size: 'small' as const,
    path: '/visualize',
  },
]

const todayStats = computed(() => ({
  questionsAsked: 8,
  conceptsLearned: 5,
  streakDays: 7,
  accuracy: 78,
  weakTopic: '图论算法',
  weakAccuracy: 35,
}))

const hotQuestions = [
  { q: '红黑树和AVL树怎么选？', tag: '高频', color: '#F43F5E' },
  { q: '虚拟内存的页面置换算法', tag: '考点', color: '#F59E0B' },
  { q: '死锁的四个必要条件', tag: '经典', color: '#7c3aed' },
  { q: 'HTTP和HTTPS的区别', tag: '必考', color: '#10B981' },
]

const mounted = ref(false)
onMounted(() => {
  requestAnimationFrame(() => {
    mounted.value = true
  })
})

function onMagneticMove(e: MouseEvent, el: HTMLElement) {
  const rect = el.getBoundingClientRect()
  const x = e.clientX - rect.left - rect.width / 2
  const y = e.clientY - rect.top - rect.height / 2
  el.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px) scale(1.02)`
}

function onMagneticLeave(el: HTMLElement) {
  el.style.transform = ''
}
</script>

<template>
  <div class="home-view" :class="{ 'is-mounted': mounted }">
    <!-- ====== Floating Particles ====== -->
    <div class="floating-particles" aria-hidden="true">
      <div class="particle p1"></div>
      <div class="particle p2"></div>
      <div class="particle p3"></div>
      <div class="particle p4"></div>
      <div class="particle p5"></div>
      <div class="particle p6"></div>
    </div>

    <!-- ====== Hero Section ====== -->
    <section class="hero-section stagger-item">
      <div class="hero-grid">
        <div class="glow-blob blob-1"></div>
        <div class="glow-blob blob-2"></div>
        <div class="glow-blob blob-3"></div>
        <div class="hero-text">
          <p class="eyebrow">
            <Sparkles :size="13" class="eyebrow-icon sparkle-icon" />
            AI 智能解题助手
            <span class="eyebrow-sep">·</span>
            距考研 218 天
          </p>
          <h1 class="hero-title">
            遇到不会的<span class="gradient-text">难题</span>？
          </h1>
          <p class="hero-lede">
            拍照、输入、描述 — AI 导师帮你彻底搞懂
          </p>
          <div class="search-box" :class="{ 'is-focused': searchFocused }" @click="searchFocused = true">
            <div class="search-box__inner">
              <input
                id="main-search-input"
                v-model="searchQuery"
                type="text"
                placeholder="输入你的问题..."
                class="search-input"
                @keydown="handleKeydown"
                @focus="searchFocused = true"
                @blur="searchFocused = false"
              />
              <button class="search-submit-btn" @mousedown.prevent="handleSearch">
                <ArrowRight :size="18" />
              </button>
            </div>
            <div class="hot-tags-row">
              <TrendingUp :size="13" class="hot-tags-icon" />
              <button
                v-for="hot in hotQuestions"
                :key="hot.q"
                class="hot-tag"
                :style="{ '--tag-color': hot.color }"
                @click="searchQuery = hot.q; handleSearch()"
              >
                {{ hot.q }}
                <span class="hot-tag__badge">{{ hot.tag }}</span>
              </button>
            </div>
          </div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <div class="hv-ring hv-ring--1"></div>
          <div class="hv-ring hv-ring--2"></div>
          <div class="hv-ring hv-ring--3"></div>
          <div class="hv-dot hv-dot--1"></div>
          <div class="hv-dot hv-dot--2"></div>
          <div class="hv-dot hv-dot--3"></div>
          <div class="hv-dot hv-dot--4"></div>
          <div class="hv-dot hv-dot--5"></div>
          <div class="hv-dot hv-dot--6"></div>
          <div class="hv-center">
            <Brain :size="32" class="hv-center-icon" />
          </div>
        </div>
      </div>
    </section>

    <!-- ====== Stats Row ====== -->
    <section class="section-spaced stagger-item">
      <p class="eyebrow">今日概览</p>
      <h2 class="section-title">学习动态</h2>
      <div class="stats-row">
        <div
          class="stat-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <p class="stat-card__value">{{ todayStats.questionsAsked }}<small> 题</small></p>
          <p class="stat-card__label">今日提问</p>
          <div class="stat-card__bar"><div class="stat-card__bar-fill" style="width:65%"></div></div>
          <p class="stat-card__sub">连续 <strong>{{ todayStats.streakDays }}</strong> 天</p>
        </div>
        <div
          class="stat-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <p class="stat-card__value">{{ todayStats.conceptsLearned }}<small> 个</small></p>
          <p class="stat-card__label">掌握概念</p>
          <div class="stat-card__bar"><div class="stat-card__bar-fill stat-card__bar-fill--green" style="width:50%"></div></div>
          <p class="stat-card__sub">今日目标 10 个</p>
        </div>
        <div
          class="stat-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <p class="stat-card__value stat-card__value--green">+{{ todayStats.accuracy }}<small>%</small></p>
          <p class="stat-card__label">答题正确率</p>
          <div class="stat-card__bar"><div class="stat-card__bar-fill stat-card__bar-fill--green" style="width:78%"></div></div>
          <p class="stat-card__sub">较昨日 +5%</p>
        </div>
      </div>
    </section>

    <!-- ====== Quick Actions ====== -->
    <section class="section-spaced stagger-item">
      <p class="eyebrow">开始学习</p>
      <h2 class="section-title">选择提问方式</h2>
      <div class="quick-actions-grid">
        <button
          v-for="(method, i) in askMethods"
          :key="method.key"
          class="qa-card"
          :class="`qa-delay-${i}`"
          :style="{ '--qa-gradient': method.gradient, '--qa-color': method.shadowColor }"
          @click="router.push(method.path)"
        >
          <div class="qa-card__icon-wrap">
            <component :is="method.icon" :size="22" class="qa-card__icon" />
          </div>
          <div class="qa-card__info">
            <span class="qa-card__label">{{ method.label }}</span>
            <span class="qa-card__desc">{{ method.desc }}</span>
          </div>
          <ChevronRight :size="15" class="qa-card__arrow" />
        </button>
      </div>
    </section>

    <!-- ====== Subjects ====== -->
    <section class="section-spaced stagger-item">
      <p class="eyebrow">按科目浏览</p>
      <h2 class="section-title">重点突破薄弱科目</h2>
      <div class="subjects-grid">
        <button
          v-for="subj in subjects"
          :key="subj.name"
          class="subject-card"
          :style="{ '--subj-color': subj.color, '--subj-bg': subj.bg }"
          @click="goToSubject(subj.name)"
        >
          <div class="subject-card__top">
            <component :is="subj.icon" :size="24" :style="{ color: subj.color }" />
            <div class="subject-card__badges">
              <span v-if="subj.hot" class="subject-card__hot">HOT</span>
              <span class="subject-card__count">{{ subj.count }}题</span>
            </div>
          </div>
          <span class="subject-card__name">{{ subj.name }}</span>
          <div class="subject-card__bar-wrap">
            <div class="subject-card__bar" :style="{ width: `${subj.progress}%`, background: subj.color }"></div>
          </div>
          <span class="subject-card__progress-text">掌握 {{ subj.progress }}%</span>
        </button>
      </div>
    </section>

    <!-- ====== Recent Questions ====== -->
    <section class="section-spaced stagger-item">
      <p class="eyebrow">继续学习</p>
      <h2 class="section-title">最近提问</h2>
      <div class="timeline-list">
        <button
          v-for="(q, i) in recentQuestions"
          :key="q.id"
          class="timeline-item"
          :class="`tl-delay-${i}`"
          @click="openQuestion(q.id)"
        >
          <div class="timeline-item__accent" :class="q.accent"></div>
          <div class="timeline-item__body">
            <p class="timeline-item__question">{{ q.question }}</p>
            <div class="timeline-item__meta">
              <span class="timeline-item__subject" :style="{ color: q.accentColor, background: `${q.accentColor}12` }">
                {{ q.subject }}
              </span>
              <span class="timeline-item__time">{{ q.time }}</span>
              <span v-if="q.replies > 0" class="timeline-item__replies">
                <MessageSquareText :size="12" /> {{ q.replies }}
              </span>
              <span v-else class="timeline-item__pending">待回答</span>
            </div>
          </div>
          <ChevronRight :size="16" class="timeline-item__arrow" />
        </button>
      </div>
    </section>

    <!-- ====== AI Powers ====== -->
    <section class="section-spaced stagger-item">
      <p class="eyebrow">AI 超能力</p>
      <h2 class="section-title">TuringMate 独家学习引擎</h2>
      <div class="powers-grid">
        <button
          v-for="(power, i) in aiPowers"
          :key="power.title"
          class="power-card"
          :class="[`power-card--${power.size}`, `pw-delay-${i}`]"
          :style="{ '--pw-color': power.color, '--pw-gradient': power.gradient }"
          @click="router.push(power.path)"
        >
          <div class="power-card__icon-ring">
            <component :is="power.icon" :size="18" class="power-card__icon" />
          </div>
          <div class="power-card__text">
            <p class="power-card__title">{{ power.title }}</p>
            <p class="power-card__desc">{{ power.desc }}</p>
          </div>
          <div class="power-card__arrow-wrap">
            <Play :size="12" class="power-card__play" />
          </div>
        </button>
      </div>
    </section>

    <!-- ====== Encouragement ====== -->
    <section class="section-spaced stagger-item">
      <div class="encouragement-card">
        <Quote :size="28" class="encouragement-card__icon" />
        <p class="encouragement-card__text">
          每一个算法都有它的美，<br />每一次坚持都离梦想更近一步。
        </p>
        <p class="encouragement-card__sub">
          已坚持学习 <strong>{{ todayStats.streakDays }}</strong> 天，继续加油
        </p>
      </div>
    </section>

    <!-- ====== Weak Topic ====== -->
    <section class="section-spaced stagger-item">
      <div class="weak-topic-card">
        <div class="weak-topic-card__icon-wrap">
          <Lightbulb :size="20" class="weak-topic-card__icon" />
        </div>
        <div class="weak-topic-card__info">
          <p class="weak-topic-card__title">
            建议优先强化 <span class="weak-topic-card__highlight">{{ todayStats.weakTopic }}</span>
          </p>
          <div class="weak-topic-card__progress-row">
            <div class="weak-topic-card__bar-bg">
              <div class="weak-topic-card__bar-fill" :style="{ width: `${todayStats.weakAccuracy}%` }"></div>
            </div>
            <span class="weak-topic-card__percent">{{ todayStats.weakAccuracy }}% 正确率</span>
          </div>
        </div>
        <button class="weak-topic-card__btn">去练习</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ============================
   1. GLOBAL: Entrance & Spacing
   ============================ */
.home-view {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.home-view.is-mounted {
  opacity: 1;
  transform: translateY(0);
}

.section-spaced {
  margin-bottom: 48px;
}

/* Stagger entrance animation */
.stagger-item {
  opacity: 0;
  transform: translateY(16px);
  animation: staggerIn 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes staggerIn {
  to { opacity: 1; transform: translateY(0); }
}

.is-mounted .stagger-item:nth-child(1) { animation-delay: 0.05s; }
.is-mounted .stagger-item:nth-child(2) { animation-delay: 0.12s; }
.is-mounted .stagger-item:nth-child(3) { animation-delay: 0.19s; }
.is-mounted .stagger-item:nth-child(4) { animation-delay: 0.26s; }
.is-mounted .stagger-item:nth-child(5) { animation-delay: 0.33s; }
.is-mounted .stagger-item:nth-child(6) { animation-delay: 0.40s; }
.is-mounted .stagger-item:nth-child(7) { animation-delay: 0.47s; }
.is-mounted .stagger-item:nth-child(8) { animation-delay: 0.54s; }
.is-mounted .stagger-item:nth-child(9) { animation-delay: 0.61s; }

/* Floating particles */
.floating-particles {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  border-radius: 50%;
  opacity: 0;
  animation: floatParticle 12s infinite ease-in-out;
}

.p1 { width: 6px; height: 6px; background: #a78bfa; top: 15%; left: 8%; animation-delay: 0s; }
.p2 { width: 4px; height: 4px; background: #34D399; top: 45%; left: 85%; animation-delay: 2s; }
.p3 { width: 5px; height: 5px; background: #F472B6; top: 70%; left: 15%; animation-delay: 4s; }
.p4 { width: 8px; height: 8px; background: #38BDF8; top: 25%; left: 92%; animation-delay: 6s; }
.p5 { width: 3px; height: 3px; background: #FBBF24; top: 80%; left: 75%; animation-delay: 8s; }
.p6 { width: 7px; height: 7px; background: #A78BFA; top: 55%; left: 5%; animation-delay: 10s; }

@keyframes floatParticle {
  0%, 100% { transform: translateY(0) scale(0); opacity: 0; }
  10% { opacity: 0.6; }
  50% { transform: translateY(-80px) scale(1); opacity: 0.4; }
  90% { opacity: 0.6; }
}

/* ============================
   2. TYPOGRAPHY: Eyebrow & Section Title
   ============================ */
.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-amber-600, #b45389);
  margin-bottom: 8px;
}

.eyebrow-icon {
  color: var(--color-amber-500, #f59e0b);
}

.eyebrow-sep {
  color: var(--color-text-muted, #d1d5db);
  font-weight: 400;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  letter-spacing: -0.015em;
  line-height: 1.3;
  margin-bottom: 16px;
}

/* ============================
   3. HERO SECTION
   ============================ */
.hero-section {
  margin-bottom: 48px;
}

.hero-grid {
  position: relative;
  display: flex;
  align-items: center;
  gap: 48px;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border-light, #eae6ef);
  border-radius: 24px;
  padding: 40px 36px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  overflow: hidden;
}

/* Glow blobs */
.glow-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.18;
  pointer-events: none;
  animation: blobDrift 8s infinite ease-in-out alternate;
}

.blob-1 {
  width: 200px; height: 200px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  top: -60px; right: -40px;
}

.blob-2 {
  width: 160px; height: 160px;
  background: linear-gradient(135deg, #a78bfa, #7c3aed);
  bottom: -50px; left: -30px;
}

.blob-3 {
  width: 100px; height: 100px;
  background: linear-gradient(135deg, #F472B6, #FB923C);
  top: 40%; left: 60%;
  animation-delay: 2s;
}

@keyframes blobDrift {
  0% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(20px, -15px) scale(1.1); }
  100% { transform: translate(-10px, 10px) scale(0.95); }
}

.hero-text {
  position: relative;
  z-index: 2;
  flex: 1;
  min-width: 0;
}

.sparkle-icon {
  animation: sparklePulse 2s infinite;
}

@keyframes sparklePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}

.hero-title {
  font-size: 36px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--color-text-primary, #111827);
  letter-spacing: -0.025em;
  margin-bottom: 10px;
}

@media (min-width: 768px) {
  .hero-title {
    font-size: 44px;
  }
}

.gradient-text {
  background: var(--gradient-text-warm, linear-gradient(135deg, #f59e0b, #b45389));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-lede {
  font-size: 15px;
  color: var(--color-text-secondary, #6b7280);
  line-height: 1.6;
  margin-bottom: 24px;
  max-width: 420px;
}

/* Search Box */
.search-box {
  border-radius: 16px;
  background: var(--color-bg-secondary, #f9fafb);
  border: 1.5px solid var(--color-border-light, #e5e7eb);
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
  overflow: hidden;
  max-width: 520px;
}

.search-box.is-focused {
  border-color: var(--color-primary, #a78bfa);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.08);
}

.search-box__inner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 5px 5px 16px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--color-text-primary, #111827);
  min-width: 0;
}

.search-input::placeholder {
  color: var(--color-text-muted, #9ca3af);
}

.search-submit-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 2px 8px rgba(124,58,237,0.25);
}

.search-submit-btn:hover {
  transform: scale(1.04);
  box-shadow: 0 4px 14px rgba(124,58,237,0.35);
}

.search-submit-btn:active {
  transform: scale(0.96);
}

/* Hot Tags */
.hot-tags-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid var(--color-border-light, #f3f4f6);
  flex-wrap: wrap;
}

.hot-tags-icon {
  color: #f59e0b;
  flex-shrink: 0;
}

.hot-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 11px;
  color: var(--color-text-secondary, #4b5563);
  background: var(--color-bg-secondary, #f3f4f6);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-tag:hover {
  color: var(--tag-color);
  background: color-mix(in srgb, var(--tag-color) 8%, #fff);
  border-color: color-mix(in srgb, var(--tag-color) 20%, transparent);
}

.hot-tag__badge {
  padding: 1px 5px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  background: color-mix(in srgb, var(--tag-color) 85%, #000);
  color: #fff;
}

/* Hero Visual — geometric brand decoration */
.hero-visual {
  position: relative;
  width: 220px;
  height: 220px;
  flex-shrink: 0;
  display: none;
}

@media (min-width: 768px) {
  .hero-visual {
    display: block;
  }
}

.hv-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 1px solid var(--color-border-light, #e5e7eb);
}

.hv-ring--1 {
  inset: 0;
}

.hv-ring--2 {
  inset: 30px;
  border-style: dashed;
  border-color: var(--color-border, #dbd7e0);
}

.hv-ring--3 {
  inset: 60px;
  border-width: 1.5px;
  border-color: color-mix(in srgb, var(--color-primary, #7c3aed) 25%, transparent);
}

.hv-dot {
  position: absolute;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-primary, #7c3aed);
  opacity: 0.5;
}

.hv-dot--1 { top: 8px; left: 50%; transform: translateX(-50%); }
.hv-dot--2 { bottom: 8px; left: 50%; transform: translateX(-50%); }
.hv-dot--3 { left: 8px; top: 50%; transform: translateY(-50%); }
.hv-dot--4 { right: 8px; top: 50%; transform: translateY(-50%); }
.hv-dot--5 { top: 36px; left: 36px; background: #f59e0b; }
.hv-dot--6 { bottom: 52px; right: 48px; background: #10b981; }

.hv-center {
  position: absolute;
  inset: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(124,58,237,0.08), rgba(167,139,250,0.04));
  display: flex;
  align-items: center;
  justify-content: center;
}

.hv-center-icon {
  color: var(--color-primary, #7c3aed);
  opacity: 0.7;
}

/* ============================
   4. STATS ROW
   ============================ */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 540px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  padding: 20px;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border-light, #f3f4f6);
  border-radius: 16px;
  transition: border-color 0.2s ease;
}

.stat-card:hover {
  border-color: var(--color-border, #dbd7e0);
}

.stat-card__value {
  font-size: 28px;
  font-weight: 800;
  color: var(--color-text-primary, #1f2937);
  line-height: 1.1;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card__value--green {
  background: linear-gradient(135deg, #10b981, #34d399);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-card__value small {
  font-size: 13px;
  font-weight: 600;
  -webkit-text-fill-color: var(--color-text-secondary, #6b7280);
}

.stat-card__label {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
  margin-bottom: 12px;
}

.stat-card__bar {
  height: 5px;
  background: rgba(124,58,237,0.08);
  border-radius: 3px;
  margin-bottom: 10px;
  overflow: hidden;
}

.stat-card__bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #7c3aed, #a78bfa);
  transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

.stat-card__bar-fill--green {
  background: linear-gradient(90deg, #10b981, #34d399);
}

.stat-card__sub {
  font-size: 11px;
  color: var(--color-text-muted, #9ca3af);
}

.stat-card__sub strong {
  color: #7c3aed;
  font-weight: 700;
}

/* ============================
   5. QUICK ACTIONS GRID
   ============================ */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (min-width: 480px) {
  .quick-actions-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.qa-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 22px 14px;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border-light, #f3f4f6);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.qa-card:hover {
  border-color: color-mix(in srgb, var(--qa-color, #7c3aed) 25%, transparent);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px color-mix(in srgb, var(--qa-color, #000) 8%, transparent);
}

.qa-card__icon-wrap {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--qa-gradient));
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.12;
  transition: opacity 0.2s;
}

.qa-card:hover .qa-card__icon-wrap {
  opacity: 0.18;
}

.qa-card__icon-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qa-card__icon {
  position: absolute;
  inset: 0;
  margin: auto;
  color: var(--color-text-secondary, #4b5563);
}

.qa-card__info {
  text-align: center;
}

.qa-card__label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary, #1f2937);
}

.qa-card__desc {
  display: block;
  font-size: 11px;
  color: var(--color-text-muted, #9ca3af);
  margin-top: 2px;
}

.qa-card__arrow {
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s;
  color: var(--color-text-muted, #d1d5db);
}

.qa-card:hover .qa-card__arrow {
  opacity: 1;
  transform: translateX(0);
}

.qa-delay-0 { animation: qaSlideIn 0.5s 0s cubic-bezier(0.22, 1, 0.36, 1) both; }
.qa-delay-1 { animation: qaSlideIn 0.5s 0.06s cubic-bezier(0.22, 1, 0.36, 1) both; }
.qa-delay-2 { animation: qaSlideIn 0.5s 0.12s cubic-bezier(0.22, 1, 0.36, 1) both; }
.qa-delay-3 { animation: qaSlideIn 0.5s 0.18s cubic-bezier(0.22, 1, 0.36, 1) both; }

@keyframes qaSlideIn {
  from { opacity: 0; transform: translateY(16px) scale(0.96); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ============================
   6. SUBJECTS GRID
   ============================ */
.subjects-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (min-width: 640px) {
  .subjects-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.subject-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 18px 16px;
  border-radius: 16px;
  background: var(--subj-bg);
  border: 1px solid color-mix(in srgb, var(--subj-color) 10%, transparent);
  cursor: pointer;
  transition: all 0.2s ease;
}

.subject-card:hover {
  border-color: color-mix(in srgb, var(--subj-color) 30%, transparent);
  box-shadow: 0 2px 12px color-mix(in srgb, var(--subj-color) 8%, transparent);
  transform: translateY(-2px);
}

.subject-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.subject-card__badges {
  display: flex;
  align-items: center;
  gap: 6px;
}

.subject-card__hot {
  padding: 2px 7px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
  color: #ef4444;
  background: rgba(239,68,68,0.1);
}

.subject-card__count {
  font-size: 11px;
  color: var(--color-text-muted, #9ca3af);
}

.subject-card__name {
  font-size: 14px;
  font-weight: 700;
  color: var(--subj-color);
}

.subject-card__bar-wrap {
  height: 4px;
  background: rgba(0,0,0,0.05);
  border-radius: 2px;
  overflow: hidden;
}

.subject-card__bar {
  height: 100%;
  border-radius: 2px;
}

.subject-card__progress-text {
  font-size: 11px;
  color: var(--color-text-muted, #9ca3af);
}

/* ============================
   7. TIMELINE LIST
   ============================ */
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: var(--color-bg-card, #fff);
  border: 1px solid transparent;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.timeline-item:hover {
  background: var(--color-bg-secondary, #fafbff);
  border-color: var(--color-border-light, #e5e7eb);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.timeline-item__accent {
  width: 4px;
  min-height: 48px;
  border-radius: 2px;
  flex-shrink: 0;
  background: linear-gradient(180deg, var(--tw-gradient-from), var(--tw-gradient-to));
}

.timeline-item__body {
  flex: 1;
  min-width: 0;
}

.timeline-item__question {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary, #1f2937);
  line-height: 1.5;
  margin-bottom: 6px;
}

.timeline-item__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.timeline-item__subject {
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
}

.timeline-item__time {
  font-size: 11px;
  color: var(--color-text-muted, #9ca3af);
}

.timeline-item__replies {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: var(--color-text-secondary, #6b7280);
}

.timeline-item__pending {
  font-size: 10px;
  font-weight: 600;
  color: #f59e0b;
  background: rgba(245,158,11,0.1);
  padding: 2px 7px;
  border-radius: 6px;
}

.timeline-item__arrow {
  flex-shrink: 0;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s;
  color: var(--color-text-muted, #d1d5db);
}

.timeline-item:hover .timeline-item__arrow {
  opacity: 1;
  transform: translateX(0);
}

.tl-delay-0 { animation: tlSlide 0.45s 0s cubic-bezier(0.22, 1, 0.36, 1) both; }
.tl-delay-1 { animation: tlSlide 0.45s 0.06s cubic-bezier(0.22, 1, 0.36, 1) both; }
.tl-delay-2 { animation: tlSlide 0.45s 0.12s cubic-bezier(0.22, 1, 0.36, 1) both; }
.tl-delay-3 { animation: tlSlide 0.45s 0.18s cubic-bezier(0.22, 1, 0.36, 1) both; }

@keyframes tlSlide {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

/* ============================
   8. AI POWERS GRID
   ============================ */
.powers-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (min-width: 640px) {
  .powers-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.power-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 16px;
  border-radius: 16px;
  background: var(--color-bg-card, #fff);
  border: 1px solid var(--color-border-light, #f3f4f6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.power-card--large {
  grid-row: span 2;
}

@media (max-width: 639px) {
  .power-card--large {
    grid-row: auto;
    grid-column: 1 / -1;
  }
}

.power-card:hover {
  border-color: color-mix(in srgb, var(--pw-color) 25%, transparent);
  box-shadow: 0 4px 20px color-mix(in srgb, var(--pw-color) 8%, transparent);
  transform: translateY(-2px);
}

.power-card__icon-ring {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--pw-gradient));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 3px 10px color-mix(in srgb, var(--pw-color) 30%, transparent);
}

.power-card__icon {
  color: #fff;
}

.power-card__title {
  font-size: 14px;
  font-weight: 700;
  color: var(--color-text-primary, #1f2937);
  line-height: 1.3;
}

.power-card__desc {
  font-size: 12px;
  color: var(--color-text-muted, #9ca3af);
  margin-top: 3px;
  line-height: 1.5;
}

.power-card__arrow-wrap {
  margin-top: auto;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-bg-secondary, #f3f4f6);
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-end;
  transition: all 0.2s ease;
  opacity: 0;
  transform: scale(0.8);
}

.power-card:hover .power-card__arrow-wrap {
  opacity: 1;
  transform: scale(1);
  background: var(--pw-color);
}

.power-card__play {
  color: var(--color-text-muted, #9ca3af);
  transition: color 0.2s;
}

.power-card:hover .power-card__play {
  color: #fff;
}

.pw-delay-0 { animation: pwPopIn 0.45s 0s cubic-bezier(0.22, 1, 0.36, 1) both; }
.pw-delay-1 { animation: pwPopIn 0.45s 0.05s cubic-bezier(0.22, 1, 0.36, 1) both; }
.pw-delay-2 { animation: pwPopIn 0.45s 0.1s cubic-bezier(0.22, 1, 0.36, 1) both; }
.pw-delay-3 { animation: pwPopIn 0.45s 0.15s cubic-bezier(0.22, 1, 0.36, 1) both; }
.pw-delay-4 { animation: pwPopIn 0.45s 0.2s cubic-bezier(0.22, 1, 0.36, 1) both; }
.pw-delay-5 { animation: pwPopIn 0.45s 0.25s cubic-bezier(0.22, 1, 0.36, 1) both; }

@keyframes pwPopIn {
  from { opacity: 0; transform: scale(0.94); }
  to { opacity: 1; transform: scale(1); }
}

/* ============================
   9. ENCOURAGEMENT
   ============================ */
.encouragement-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 32px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(245,158,11,0.04), rgba(124,58,237,0.03));
  border: 1px solid rgba(245,158,11,0.1);
}

.encouragement-card__icon {
  color: var(--color-amber-400, #fbbf24);
  opacity: 0.5;
  margin-bottom: 12px;
}

.encouragement-card__text {
  font-size: 1.15rem;
  line-height: 1.8;
  color: var(--color-text-primary);
  letter-spacing: 0.04em;
  margin-bottom: 8px;
  font-family: var(--font-serif, 'Noto Serif SC', 'Source Han Serif SC', serif);
}

.encouragement-card__sub {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.encouragement-card__sub strong {
  color: var(--color-amber-600, #d97706);
  font-weight: 700;
}

/* ============================
   10. WEAK TOPIC
   ============================ */
.weak-topic-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(239,68,68,0.04), rgba(249,115,22,0.03));
  border: 1px solid rgba(239,68,68,0.1);
  transition: border-color 0.2s ease;
  animation: weakPulse 3s infinite ease-in-out;
}

@keyframes weakPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.1); }
  50% { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}

.weak-topic-card:hover {
  animation: none;
}

.weak-topic-card:hover {
  border-color: rgba(239,68,68,0.2);
}

.weak-topic-card__icon-wrap {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #fca5a5, #f87171);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 3px 12px rgba(239,68,68,0.2);
}

.weak-topic-card__icon {
  color: #fff;
}

.weak-topic-card__info {
  flex: 1;
  min-width: 0;
}

.weak-topic-card__title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-primary, #374151);
  margin-bottom: 8px;
}

.weak-topic-card__highlight {
  color: #ef4444;
  font-weight: 700;
}

.weak-topic-card__progress-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.weak-topic-card__bar-bg {
  flex: 1;
  height: 5px;
  background: rgba(239,68,68,0.1);
  border-radius: 3px;
  overflow: hidden;
  max-width: 140px;
}

.weak-topic-card__bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #fca5a5, #ef4444);
}

.weak-topic-card__percent {
  font-size: 12px;
  font-weight: 700;
  color: #ef4444;
}

.weak-topic-card__btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #f87171, #ef4444);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(239,68,68,0.25);
}

.weak-topic-card__btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(239,68,68,0.35);
}

.weak-topic-card__btn:active {
  transform: scale(0.97);
}

/* ============================
   11. RESPONSIVE
   ============================ */
@media (max-width: 480px) {
  .hero-grid {
    padding: 28px 20px;
  }
  .hero-title {
    font-size: 28px;
  }
  .section-spaced {
    margin-bottom: 32px;
  }
  .weak-topic-card {
    flex-direction: column;
    align-items: flex-start;
  }
  .weak-topic-card__btn {
    width: 100%;
    text-align: center;
  }
  .weak-topic-card__bar-bg {
    max-width: 100%;
  }
}
</style>
