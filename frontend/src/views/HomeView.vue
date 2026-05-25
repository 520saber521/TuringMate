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
} from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'

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
  { name: '数据结构', icon: '🌲', color: '#6366F1', bg: 'rgba(99,102,241,0.08)', count: 128, hot: true, progress: 65 },
  { name: '计组', icon: '⚙️', color: '#0EA5E9', bg: 'rgba(14,165,233,0.08)', count: 96, hot: false, progress: 42 },
  { name: '操作系统', icon: '💻', color: '#10B981', bg: 'rgba(16,185,129,0.08)', count: 84, hot: true, progress: 78 },
  { name: '网络', icon: '🌐', color: '#F43F5E', bg: 'rgba(244,63,94,0.08)', count: 72, hot: false, progress: 30 },
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
    accentColor: '#6366F1',
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
    color: '#6366F1',
    gradient: 'from-indigo-500 via-violet-500 to-purple-500',
    size: 'large' as const,
    path: '/chat/demo',
  },
  {
    title: '举一反三',
    desc: '一道题变出N道变体，举一反三',
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
    color: '#8B5CF6',
    gradient: 'from-violet-500 via-purple-500 to-fuchsia-500',
    size: 'small' as const,
    path: '/diagnosis',
  },
  {
    title: 'AI 研友',
    desc: '虚拟学习伙伴陪你讨论问题，互帮互助',
    icon: Users,
    color: '#10B981',
    gradient: 'from-emerald-500 via-green-500 to-teal-500',
    size: 'small' as const,
    path: '/chat/demo',
  },
  {
    title: '情绪感知',
    desc: '懂你心情的智能导师，适时调整教学节奏',
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
  { q: '死锁的四个必要条件', tag: '经典', color: '#6366F1' },
  { q: 'HTTP和HTTPS的区别', tag: '必考', color: '#10B981' },
]

// Entrance animation trigger
const mounted = ref(false)
onMounted(() => {
  requestAnimationFrame(() => {
    mounted.value = true
  })
})

// Magnetic hover effect
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
    <!-- ====== Floating Particles Background ====== -->
    <div class="floating-particles" aria-hidden="true">
      <div class="particle p1"></div>
      <div class="particle p2"></div>
      <div class="particle p3"></div>
      <div class="particle p4"></div>
      <div class="particle p5"></div>
      <div class="particle p6"></div>
    </div>

    <!-- ====== Hero Section ====== -->
    <section class="hero-section mb-8 stagger-item">
      <div class="hero-card">
        <!-- Multi-color glow blobs -->
        <div class="glow-blob blob-1"></div>
        <div class="glow-blob blob-2"></div>
        <div class="glow-blob blob-3"></div>

        <div class="hero-content">
          <!-- Status row -->
          <div class="flex items-center gap-3 mb-5 flex-wrap">
            <div class="status-badge status-badge--ai">
              <Sparkles :size="14" class="sparkle-icon" />
              <span>AI 智能解题助手 v2.0</span>
            </div>
            <span class="countdown-badge">
              <span class="countdown-dot"></span>
              距考研 218 天
            </span>
          </div>

          <!-- Title -->
          <h1 class="hero-title">
            遇到不会的
            <span class="gradient-text gradient-text--fire">难题</span>
            ？
          </h1>
          <p class="hero-subtitle">
            拍照、输入、描述 — 三种方式，AI 导师帮你彻底搞懂
          </p>

          <!-- Search Box -->
          <div
            class="search-box"
            :class="{ 'is-focused': searchFocused }"
            @click="searchFocused = true"
          >
            <div class="search-box__inner">
              <div class="search-icon-wrap">
                <Camera :size="20" class="search-icon" />
              </div>
              <input
                id="main-search-input"
                v-model="searchQuery"
                type="text"
                placeholder="输入你想问的问题..."
                class="search-input"
                @keydown="handleKeydown"
                @focus="searchFocused = true"
                @blur="searchFocused = false"
              />
              <button
                class="search-submit-btn"
                @mousedown.prevent="handleSearch"
              >
                <ArrowRight :size="18" />
                <span class="search-submit-ripple"></span>
              </button>
            </div>
            <!-- Hot Tags -->
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
      </div>
    </section>

    <!-- ====== Feature Banner: Asymmetric Layout ====== -->
    <section class="feature-banner mb-8 stagger-item">
      <div class="feature-banner__grid">
        <!-- Left: large stat card -->
        <div
          class="feature-stat-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <div class="feature-stat-card__glow"></div>
          <div class="feature-stat-card__content">
            <div class="feature-stat-card__icon">
              <BarChart3 :size="22" />
            </div>
            <div class="feature-stat-card__value">
              <span class="feature-stat-card__number">{{ todayStats.questionsAsked }}</span>
              <span class="feature-stat-card__unit">题</span>
            </div>
            <p class="feature-stat-card__label">今日提问</p>
            <div class="feature-stat-card__progress">
              <div class="feature-stat-card__bar" :style="{ width: '65%' }"></div>
            </div>
            <p class="feature-stat-card__sub">连续学习 <strong>{{ todayStats.streakDays }}</strong> 天 🔥</p>
          </div>
        </div>

        <!-- Right top: concept mastery -->
        <div
          class="feature-mini-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <div class="feature-mini-card__icon feature-mini-card__icon--green">
            <Star :size="16" />
          </div>
          <div>
            <p class="feature-mini-card__value">{{ todayStats.conceptsLearned }}</p>
            <p class="feature-mini-card__label">今日掌握概念</p>
          </div>
        </div>

        <!-- Right bottom: accuracy -->
        <div
          class="feature-mini-card magnetic-card"
          @mousemove="(e) => onMagneticMove(e, ($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
          @mouseleave="(e) => onMagneticLeave(($event.target as HTMLElement).closest('.magnetic-card') as HTMLElement)"
        >
          <div class="feature-mini-card__icon feature-mini-card__icon--blue">
            <Target :size="16" />
          </div>
          <div>
            <p class="feature-mini-card__value feature-mini-card__value--green">+{{ todayStats.accuracy }}%</p>
            <p class="feature-mini-card__label">答题正确率</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ====== Quick Actions: Staggered 2-col Grid ====== -->
    <section class="mb-8 stagger-item">
      <div class="section-header">
        <div>
          <h3 class="section-title">开始学习</h3>
          <p class="section-desc">选择最适合你的提问方式</p>
        </div>
      </div>
      <div class="quick-actions-grid">
        <button
          v-for="(method, i) in askMethods"
          :key="method.key"
          class="quick-action-card"
          :class="`qa-delay-${i}`"
          :style="{
            '--card-gradient': method.gradient,
            '--card-shadow': method.shadowColor,
          }"
          @click="router.push(method.path)"
        >
          <div class="quick-action-card__icon-wrap">
            <div class="quick-action-card__icon-bg"></div>
            <component :is="method.icon" :size="22" class="quick-action-card__icon" />
          </div>
          <div class="quick-action-card__info">
            <span class="quick-action-card__label">{{ method.label }}</span>
            <span class="quick-action-card__desc">{{ method.desc }}</span>
          </div>
          <ChevronRight :size="16" class="quick-action-card__arrow" />
        </button>
      </div>
    </section>

    <!-- ====== Subjects: Magazine-style Cards ====== -->
    <section class="mb-8 stagger-item">
      <div class="section-header">
        <div>
          <h3 class="section-title">按科目浏览</h3>
          <p class="section-desc">选择你的薄弱科目重点突破</p>
        </div>
        <button class="section-link-btn">
          全部科目 <ChevronRight :size="14" />
        </button>
      </div>
      <div class="subjects-grid">
        <button
          v-for="subj in subjects"
          :key="subj.name"
          class="subject-card"
          :style="{ '--subj-color': subj.color, '--subj-bg': subj.bg }"
          @click="goToSubject(subj.name)"
        >
          <div class="subject-card__top">
            <span class="subject-card__emoji">{{ subj.icon }}</span>
            <div class="subject-card__badges">
              <span v-if="subj.hot" class="subject-card__hot">HOT</span>
              <span class="subject-card__count">{{ subj.count }}题</span>
            </div>
          </div>
          <span class="subject-card__name">{{ subj.name }}</span>
          <div class="subject-card__bar-wrap">
            <div
              class="subject-card__bar"
              :style="{ width: `${subj.progress}%`, background: subj.color }"
            ></div>
          </div>
          <span class="subject-card__progress-text">掌握 {{ subj.progress }}%</span>
        </button>
      </div>
    </section>

    <!-- ====== Recent Questions: Timeline Layout ====== -->
    <section class="mb-8 stagger-item">
      <div class="section-header">
        <div>
          <h3 class="section-title">最近提问</h3>
          <p class="section-desc">继续未完成的讨论</p>
        </div>
        <button class="section-link-btn">
          查看全部 <ChevronRight :size="14" />
        </button>
      </div>
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
              <span
                class="timeline-item__subject"
                :style="{ color: q.accentColor, background: `${q.accentColor}12` }"
              >
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

    <!-- ====== AI Powers: Masonry Grid ====== -->
    <section class="mb-8 stagger-item">
      <div class="section-header">
        <div class="flex items-center gap-2">
          <Zap :size="18" class="text-amber-500" />
          <div>
            <h3 class="section-title">AI 超能力</h3>
            <p class="section-desc">TuringMate 独家智能学习引擎</p>
          </div>
        </div>
      </div>
      <div class="powers-masonry">
        <button
          v-for="(power, i) in aiPowers"
          :key="power.title"
          class="power-card"
          :class="[
            `power-card--${power.size}`,
            `pw-delay-${i}`,
          ]"
          :style="{
            '--pw-color': power.color,
            '--pw-gradient': power.gradient,
          }"
          @click="router.push(power.path)"
        >
          <div class="power-card__glow"></div>
          <div class="power-card__icon-ring">
            <component :is="power.icon" :size="20" class="power-card__icon" />
          </div>
          <div class="power-card__text">
            <p class="power-card__title">{{ power.title }}</p>
            <p class="power-card__desc">{{ power.desc }}</p>
          </div>
          <div class="power-card__arrow-wrap">
            <Play :size="14" class="power-card__play" />
          </div>
        </button>
      </div>
    </section>

    <!-- ====== Weak Topic Alert ====== -->
    <section class="pb-6 stagger-item">
      <div class="weak-topic-card">
        <div class="weak-topic-card__icon-wrap">
          <Lightbulb :size="22" class="weak-topic-card__icon" />
        </div>
        <div class="weak-topic-card__info">
          <p class="weak-topic-card__title">
            建议优先强化 <span class="weak-topic-card__highlight">{{ todayStats.weakTopic }}</span>
          </p>
          <div class="weak-topic-card__progress-row">
            <div class="weak-topic-card__bar-bg">
              <div
                class="weak-topic-card__bar-fill"
                :style="{ width: `${todayStats.weakAccuracy}%` }"
              ></div>
            </div>
            <span class="weak-topic-card__percent">{{ todayStats.weakAccuracy }}% 正确率</span>
          </div>
        </div>
        <button class="weak-topic-card__btn">
          去练习
          <span class="weak-topic-card__btn-ripple"></span>
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* ============================
   1. BASE & PARTICLES
   ============================ */
.home-view {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}

.home-view.is-mounted {
  opacity: 1;
  transform: translateY(0);
}

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

.p1 { width: 6px; height: 6px; background: #818CF8; top: 15%; left: 8%; animation-delay: 0s; }
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
   2. HERO SECTION
   ============================ */
.hero-section {
  position: relative;
  z-index: 1;
}

.hero-card {
  position: relative;
  background: #fff;
  border-radius: 24px;
  padding: 32px 28px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 4px 30px rgba(0,0,0,0.04);
  transition: box-shadow 0.3s ease;
}

.hero-card:hover {
  box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}

/* Multi-color glow blobs */
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
  background: linear-gradient(135deg, #818CF8, #A78BFA);
  top: -60px; right: -40px;
}

.blob-2 {
  width: 160px; height: 160px;
  background: linear-gradient(135deg, #34D399, #6EE7B7);
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

.hero-content {
  position: relative;
  z-index: 2;
}

/* Status badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge--ai {
  background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
  color: #4F46E5;
  border: 1px solid #C7D2FE;
}

.sparkle-icon {
  animation: sparklePulse 2s infinite;
}

@keyframes sparklePulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.85); }
}

.countdown-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: #6B7280;
  background: #F9FAFB;
  border: 1px solid #E5E7EB;
}

.countdown-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10B981;
  animation: dotPulse 2s infinite;
}

@keyframes dotPulse {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
  50% { opacity: 0.6; box-shadow: 0 0 0 6px rgba(16,185,129,0); }
}

/* Hero title */
.hero-title {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.25;
  color: #111827;
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

@media (min-width: 768px) {
  .hero-title { font-size: 34px; }
}

.gradient-text--fire {
  background: linear-gradient(135deg, #F97316 0%, #EF4444 50%, #8B5CF6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 14px;
  color: #6B7280;
  margin-bottom: 24px;
  line-height: 1.6;
}

/* Search Box */
.search-box {
  border-radius: 18px;
  background: #F9FAFB;
  border: 2px solid #E5E7EB;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  overflow: hidden;
}

.search-box.is-focused {
  border-color: #818CF8;
  background: #fff;
  box-shadow: 0 0 0 4px rgba(129,140,248,0.1), 0 8px 30px rgba(99,102,241,0.12);
}

.search-box__inner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px;
}

.search-icon-wrap {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #EEF2FF, #E0E7FF);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.search-icon {
  color: #6366F1;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: #111827;
  min-width: 0;
}

.search-input::placeholder {
  color: #9CA3AF;
}

.search-submit-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 2px 12px rgba(99,102,241,0.35);
}

.search-submit-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(99,102,241,0.5);
}

.search-submit-btn:active {
  transform: scale(0.95);
}

.search-submit-ripple {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}

.search-submit-btn:hover .search-submit-ripple {
  opacity: 1;
}

/* Hot Tags */
.hot-tags-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-top: 1px solid #F3F4F6;
  flex-wrap: wrap;
}

.hot-tags-icon {
  color: #F59E0B;
  flex-shrink: 0;
}

.hot-tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 11px;
  color: #4B5563;
  background: #F3F4F6;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hot-tag:hover {
  color: var(--tag-color);
  background: color-mix(in srgb, var(--tag-color) 8%, #fff);
  border-color: color-mix(in srgb, var(--tag-color) 20%, transparent);
  transform: translateY(-1px);
}

.hot-tag__badge {
  padding: 1px 5px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 600;
  background: color-mix(in srgb, var(--tag-color) 85%, #000);
  color: #fff;
}

/* ============================
   3. FEATURE BANNER (Asymmetric)
   ============================ */
.feature-banner__grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  grid-template-rows: auto auto;
  gap: 12px;
}

@media (max-width: 640px) {
  .feature-banner__grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto auto;
  }
}

/* Large stat card */
.feature-stat-card {
  grid-row: 1 / 3;
  position: relative;
  background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 50%, #FDF2F8 100%);
  border-radius: 20px;
  padding: 24px;
  border: 1px solid rgba(99,102,241,0.12);
  cursor: pointer;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}

@media (max-width: 640px) {
  .feature-stat-card {
    grid-column: 1 / -1;
    grid-row: auto;
  }
}

.feature-stat-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 30% 20%, rgba(99,102,241,0.12), transparent 60%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.feature-stat-card:hover .feature-stat-card__glow {
  opacity: 1;
}

.feature-stat-card__content {
  position: relative;
  z-index: 1;
}

.feature-stat-card__icon {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366F1, #8B5CF6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-bottom: 16px;
  box-shadow: 0 4px 14px rgba(99,102,241,0.3);
}

.feature-stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.feature-stat-card__number {
  font-size: 42px;
  font-weight: 800;
  color: #1F2937;
  line-height: 1;
  background: linear-gradient(135deg, #6366F1, #A78BFA);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.feature-stat-card__unit {
  font-size: 14px;
  font-weight: 600;
  color: #6B7280;
}

.feature-stat-card__label {
  font-size: 13px;
  color: #6B7280;
  margin-bottom: 16px;
}

.feature-stat-card__progress {
  height: 6px;
  background: rgba(99,102,241,0.12);
  border-radius: 3px;
  margin-bottom: 12px;
  overflow: hidden;
}

.feature-stat-card__bar {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #6366F1, #A78BFA);
  animation: barGrow 1.2s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}

@keyframes barGrow {
  from { width: 0 !important; }
}

.feature-stat-card__sub {
  font-size: 12px;
  color: #9CA3AF;
}

.feature-stat-card__sub strong {
  color: #6366F1;
  font-weight: 700;
}

/* Mini cards */
.feature-mini-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #F3F4F6;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.feature-mini-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  border-color: #E5E7EB;
}

.feature-mini-card__icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
}

.feature-mini-card__icon--green {
  background: linear-gradient(135deg, #34D399, #10B981);
  box-shadow: 0 3px 10px rgba(16,185,129,0.25);
}

.feature-mini-card__icon--blue {
  background: linear-gradient(135deg, #38BDF8, #0EA5E9);
  box-shadow: 0 3px 10px rgba(14,165,233,0.25);
}

.feature-mini-card__value {
  font-size: 22px;
  font-weight: 800;
  color: #1F2937;
  line-height: 1.2;
}

.feature-mini-card__value--green {
  color: #10B981;
}

.feature-mini-card__label {
  font-size: 12px;
  color: #9CA3AF;
}

/* ============================
   4. SECTION HEADERS
   ============================ */
.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 16px;
}

.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #111827;
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.section-desc {
  font-size: 13px;
  color: #9CA3AF;
  margin-top: 2px;
}

.section-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #6366F1;
  background: #EEF2FF;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.section-link-btn:hover {
  background: #E0E7FF;
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

.quick-action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 20px 12px;
  background: #fff;
  border: 1px solid #F3F4F6;
  border-radius: 20px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  overflow: hidden;
}

.quick-action-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, var(--card-gradient));
  opacity: 0;
  transition: opacity 0.35s ease;
  z-index: 0;
}

.quick-action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px var(--card-shadow);
  border-color: transparent;
}

.quick-action-card:hover::before {
  opacity: 0.04;
}

.quick-action-card:active {
  transform: translateY(-1px) scale(0.98);
}

.quick-action-card > * {
  position: relative;
  z-index: 1;
}

.quick-action-card__icon-wrap {
  position: relative;
  width: 48px;
  height: 48px;
}

.quick-action-card__icon-bg {
  position: absolute;
  inset: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--card-gradient));
  opacity: 0.12;
  transition: opacity 0.3s, transform 0.3s;
}

.quick-action-card:hover .quick-action-card__icon-bg {
  opacity: 0.2;
  transform: scale(1.1);
}

.quick-action-card__icon {
  position: absolute;
  inset: 0;
  margin: auto;
  color: #4B5563;
  transition: all 0.3s;
}

.quick-action-card:hover .quick-action-card__icon {
  color: #1F2937;
}

.quick-action-card__label {
  font-size: 13px;
  font-weight: 700;
  color: #1F2937;
}

.quick-action-card__desc {
  font-size: 11px;
  color: #9CA3AF;
  text-align: center;
}

.quick-action-card__arrow {
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.3s;
  color: #D1D5DB;
}

.quick-action-card:hover .quick-action-card__arrow {
  opacity: 1;
  transform: translateX(0);
}

/* Staggered delays */
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
  border-radius: 18px;
  background: var(--subj-bg);
  border: 1px solid color-mix(in srgb, var(--subj-color) 10%, transparent);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.subject-card:hover {
  border-color: color-mix(in srgb, var(--subj-color) 30%, transparent);
  box-shadow: 0 4px 16px color-mix(in srgb, var(--subj-color) 12%, transparent);
  transform: translateY(-2px);
}

.subject-card__top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.subject-card__emoji {
  font-size: 28px;
  line-height: 1;
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
  color: #EF4444;
  background: rgba(239,68,68,0.1);
}

.subject-card__count {
  font-size: 11px;
  color: #9CA3AF;
}

.subject-card__name {
  font-size: 14px;
  font-weight: 700;
  color: var(--subj-color);
}

.subject-card__bar-wrap {
  height: 4px;
  background: rgba(0,0,0,0.06);
  border-radius: 2px;
  overflow: hidden;
}

.subject-card__bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
}

.subject-card__progress-text {
  font-size: 11px;
  color: #9CA3AF;
}

/* ============================
   7. TIMELINE LIST
   ============================ */
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  background: #fff;
  border: 1px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.timeline-item:hover {
  background: #FAFBFF;
  border-color: #E5E7EB;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
  transform: translateX(4px);
}

.timeline-item:active {
  transform: translateX(2px) scale(0.995);
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
  color: #1F2937;
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
  color: #9CA3AF;
}

.timeline-item__replies {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 11px;
  color: #6B7280;
}

.timeline-item__pending {
  font-size: 10px;
  font-weight: 600;
  color: #F59E0B;
  background: rgba(245,158,11,0.1);
  padding: 2px 7px;
  border-radius: 6px;
}

.timeline-item__arrow {
  flex-shrink: 0;
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.3s;
  color: #D1D5DB;
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
   8. AI POWERS MASONRY
   ============================ */
.powers-masonry {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

@media (min-width: 640px) {
  .powers-masonry {
    grid-template-columns: repeat(3, 1fr);
  }
}

.power-card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 16px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #F3F4F6;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
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

.power-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, color-mix(in srgb, var(--pw-color) 15%, transparent), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.power-card:hover .power-card__glow {
  opacity: 1;
}

.power-card:hover {
  border-color: color-mix(in srgb, var(--pw-color) 25%, transparent);
  box-shadow: 0 8px 30px color-mix(in srgb, var(--pw-color) 12%, transparent);
  transform: translateY(-3px);
}

.power-card:active {
  transform: translateY(-1px) scale(0.99);
}

.power-card > * {
  position: relative;
  z-index: 1;
}

.power-card__icon-ring {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--pw-gradient));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px color-mix(in srgb, var(--pw-color) 35%, transparent);
  transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
}

.power-card:hover .power-card__icon-ring {
  transform: scale(1.08) rotate(-3deg);
}

.power-card__icon {
  color: #fff;
}

.power-card__title {
  font-size: 14px;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.3;
}

.power-card__desc {
  font-size: 12px;
  color: #9CA3AF;
  margin-top: 3px;
  line-height: 1.5;
}

.power-card__arrow-wrap {
  margin-top: auto;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  align-self: flex-end;
  transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
  opacity: 0;
  transform: scale(0.8);
}

.power-card:hover .power-card__arrow-wrap {
  opacity: 1;
  transform: scale(1);
  background: var(--pw-color);
}

.power-card__play {
  color: #9CA3AF;
  transition: color 0.3s;
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
   9. WEAK TOPIC CARD
   ============================ */
.weak-topic-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 20px;
  background: linear-gradient(135deg, #FEF2F2, #FFF7ED);
  border: 1px solid rgba(239,68,68,0.15);
  transition: all 0.3s ease;
  animation: weakPulse 3s infinite ease-in-out;
}

@keyframes weakPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.1); }
  50% { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
}

.weak-topic-card:hover {
  border-color: rgba(239,68,68,0.3);
  animation: none;
}

.weak-topic-card__icon-wrap {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, #FCA5A5, #F87171);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(239,68,68,0.3);
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
  color: #374151;
  margin-bottom: 8px;
}

.weak-topic-card__highlight {
  color: #EF4444;
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
  background: rgba(239,68,68,0.12);
  border-radius: 3px;
  overflow: hidden;
  max-width: 140px;
}

.weak-topic-card__bar-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #FCA5A5, #EF4444);
  transition: width 1s cubic-bezier(0.22, 1, 0.36, 1);
}

.weak-topic-card__percent {
  font-size: 12px;
  font-weight: 700;
  color: #EF4444;
}

.weak-topic-card__btn {
  padding: 10px 20px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #F87171, #EF4444);
  border: none;
  cursor: pointer;
  flex-shrink: 0;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
  box-shadow: 0 3px 12px rgba(239,68,68,0.3);
}

.weak-topic-card__btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(239,68,68,0.4);
}

.weak-topic-card__btn:active {
  transform: scale(0.96);
}

.weak-topic-card__btn-ripple {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s;
}

.weak-topic-card__btn:hover .weak-topic-card__btn-ripple {
  opacity: 1;
}

/* ============================
   10. RESPONSIVE
   ============================ */
@media (max-width: 480px) {
  .hero-card { padding: 24px 18px; }
  .hero-title { font-size: 24px; }
  .weak-topic-card { flex-direction: column; align-items: flex-start; }
  .weak-topic-card__btn { width: 100%; text-align: center; }
  .weak-topic-card__bar-bg { max-width: 100%; }
}
</style>
