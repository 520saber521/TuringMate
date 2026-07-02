<script setup lang="ts">
/**
 * TopNav — 顶部水平导航栏
 * 替代原侧边栏 AppSidebar
 * 设计：12 项导航项，桌面端水平排列，移动端横向滚动
 */
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Camera,
  BarChart3,
  Code2,
  MessageCircle,
  Users,
  Route,
  BookOpen,
  Sparkles,
  Library,
  Network,
  Flame,
  Play,
  Pause,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'
import { useStudyTimerStore } from '@/stores/studyTimer'

const route = useRoute()
const router = useRouter()
const timer = useStudyTimerStore()

// 横向滚动引用
const navScrollRef = ref<HTMLElement | null>(null)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)

const navItems = [
  { path: '/home', icon: Home, label: '首页', desc: '回到主页' },
  { path: '/bank', icon: Library, label: '题库', desc: '海量真题' },
  { path: '/wiki', icon: Network, label: '知识点', desc: '知识树' },
  { path: '/community', icon: Users, label: '社区', desc: '讨论交流' },
  { path: '/chat/ask', icon: MessageCircle, label: 'AI 对话', desc: '智能问答' },
  { path: '/camera', icon: Camera, label: '拍照识别', desc: '拍照搜题' },
  { path: '/visualize', icon: Code2, label: '代码实战', desc: '在线编程' },
  { path: '/problem-gen', icon: Sparkles, label: '举一反三', desc: '智能出题' },
  { path: '/diagnosis', icon: BarChart3, label: '薄弱诊断', desc: '精准分析' },
  { path: '/mistake-book', icon: BookOpen, label: '错题本', desc: '查漏补缺' },
  { path: '/learning-path', icon: Route, label: '学习路径', desc: '规划路线' },
]

const activePath = computed(() => {
  if (route.path.startsWith('/chat')) return '/chat/ask'
  return route.path
})

function navigate(path: string) {
  if (route.path === path) return
  router.push(path)
}

function checkScroll() {
  const el = navScrollRef.value
  if (!el) return
  canScrollLeft.value = el.scrollLeft > 4
  canScrollRight.value = el.scrollLeft < el.scrollWidth - el.clientWidth - 4
}

function scrollBy(direction: 'left' | 'right') {
  const el = navScrollRef.value
  if (!el) return
  const amount = direction === 'left' ? -200 : 200
  el.scrollBy({ left: amount, behavior: 'smooth' })
}

// 滚动到激活项
function scrollToActive() {
  const el = navScrollRef.value
  if (!el) return
  const activeBtn = el.querySelector('.topnav-item.is-active') as HTMLElement
  if (activeBtn) {
    activeBtn.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }
}
</script>

<template>
  <div class="topnav-bar">
    <!-- 左侧：导航滚动区 -->
    <div class="topnav-scroll-wrapper">
      <button
        v-show="canScrollLeft"
        class="scroll-btn scroll-btn--left"
        aria-label="向左滚动"
        @click="scrollBy('left')"
      >
        <ChevronLeft :size="16" />
      </button>

      <nav
        ref="navScrollRef"
        class="topnav-scroll"
        @scroll="checkScroll"
      >
        <button
          v-for="(item, index) in navItems"
          :key="item.path"
          :class="['topnav-item', { 'is-active': activePath === item.path }]"
          :style="{ '--idx': index }"
          @click="navigate(item.path)"
        >
          <!-- 底部激活指示条 -->
          <span class="active-underline"></span>

          <!-- 图标 -->
          <component :is="item.icon" :size="16" class="item-icon" />

          <!-- 文字 -->
          <span class="item-label">{{ item.label }}</span>
        </button>
      </nav>

      <button
        v-show="canScrollRight"
        class="scroll-btn scroll-btn--right"
        aria-label="向右滚动"
        @click="scrollBy('right')"
      >
        <ChevronRight :size="16" />
      </button>
    </div>

    <!-- 右侧：今日学习迷你卡 -->
    <div class="topnav-study">
      <div class="study-pill">
        <div class="study-pill__icon" :class="{ active: timer.pomodoroRunning }">
          <Flame :size="14" />
        </div>
        <div class="study-pill__body">
          <div class="study-pill__time-row">
            <span class="study-pill__time">{{ timer.todayMinutes }}</span>
            <span class="study-pill__unit">分钟</span>
          </div>
          <div class="study-pill__progress">
            <div
              class="study-pill__fill"
              :style="{ width: `${Math.min(timer.progressPercent, 100)}%` }"
            ></div>
          </div>
        </div>
        <button
          v-if="!timer.pomodoroRunning"
          class="study-pill__btn study-pill__btn--start"
          :aria-label="timer.pomodoroPhase === 'idle' ? '开始专注' : '继续专注'"
          @click="timer.startFocus()"
        >
          <Play :size="12" />
        </button>
        <button
          v-else
          class="study-pill__btn study-pill__btn--pause"
          aria-label="暂停"
          @click="timer.pausePomodoro()"
        >
          <Pause :size="12" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ============================================
   TOP NAV BAR — 顶部水平导航
   ============================================ */

.topnav-bar {
  position: fixed;
  top: 4.5rem;
  left: 0;
  right: 0;
  z-index: 45;
  height: 3.25rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1.25rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(15, 23, 42, 0.06);
}

@media (min-width: 768px) {
  .topnav-bar {
    padding: 0 1.5rem;
  }
}

@media (min-width: 1024px) {
  .topnav-bar {
    padding: 0 2rem;
  }
}

/* ===== 滚动区 ===== */
.topnav-scroll-wrapper {
  flex: 1;
  min-width: 0;
  position: relative;
  display: flex;
  align-items: center;
}

.topnav-scroll {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  overflow-x: auto;
  overflow-y: hidden;
  scroll-behavior: smooth;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: 0 0.25rem;
  min-width: 0;
}

.topnav-scroll::-webkit-scrollbar {
  display: none;
}

/* 滚动箭头 */
.scroll-btn {
  position: absolute;
  z-index: 2;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: white;
  border: 1px solid rgba(15, 23, 42, 0.08);
  color: #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.2s ease;
}

.scroll-btn:hover {
  background: #f8fafc;
  color: #0d9488;
  border-color: rgba(13, 148, 136, 0.2);
}

.scroll-btn--left {
  left: -0.625rem;
}

.scroll-btn--right {
  right: -0.625rem;
}

/* ===== 导航项 ===== */
.topnav-item {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 0.4375rem;
  flex-shrink: 0;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: #64748b;
  font-size: 0.8125rem;
  font-weight: 500;
  font-family: inherit;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s ease;
  animation: navFadeIn 0.4s ease backwards;
  animation-delay: calc(var(--idx) * 25ms);
}

@keyframes navFadeIn {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.topnav-item:hover {
  background: rgba(15, 23, 42, 0.04);
  color: #0f172a;
}

/* 激活态 */
.topnav-item.is-active {
  background: rgba(13, 148, 136, 0.08);
  color: #0d9488;
  font-weight: 600;
}

.topnav-item.is-active:hover {
  background: rgba(13, 148, 136, 0.1);
}

/* 底部激活线 */
.active-underline {
  position: absolute;
  left: 50%;
  bottom: -0.25rem;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #0d9488;
  border-radius: 999px 999px 0 0;
  transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.topnav-item.is-active .active-underline {
  width: 60%;
}

.item-icon {
  flex-shrink: 0;
}

.item-label {
  letter-spacing: -0.005em;
}

/* ===== 今日学习胶囊 ===== */
.topnav-study {
  flex-shrink: 0;
}

.study-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem 0.25rem 0.25rem;
  background: #f8fafc;
  border: 1px solid rgba(15, 23, 42, 0.06);
  border-radius: 999px;
  height: 2.25rem;
  transition: all 0.2s ease;
}

.study-pill:hover {
  background: #f1f5f9;
  border-color: rgba(15, 23, 42, 0.1);
}

.study-pill__icon {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.study-pill__icon.active {
  background: #0d9488;
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(13, 148, 136, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(13, 148, 136, 0); }
}

.study-pill__body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.study-pill__time-row {
  display: flex;
  align-items: baseline;
  gap: 2px;
  line-height: 1;
}

.study-pill__time {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0f172a;
  font-feature-settings: "tnum";
  line-height: 1;
}

.study-pill__unit {
  font-size: 0.6875rem;
  color: #94a3b8;
  font-weight: 500;
}

.study-pill__progress {
  width: 60px;
  height: 3px;
  background: rgba(15, 23, 42, 0.06);
  border-radius: 999px;
  overflow: hidden;
}

.study-pill__fill {
  height: 100%;
  background: linear-gradient(90deg, #0d9488, #14b8a6);
  border-radius: 999px;
  transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.study-pill__btn {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.study-pill__btn--start {
  background: #0d9488;
  color: white;
}

.study-pill__btn--start:hover {
  background: #0f766e;
  transform: scale(1.05);
}

.study-pill__btn--pause {
  background: #fef3c7;
  color: #92400e;
}

.study-pill__btn--pause:hover {
  background: #fde68a;
}

/* ===== 响应式 ===== */

/* 小屏：紧凑模式，隐藏描述 */
@media (max-width: 640px) {
  .topnav-bar {
    padding: 0 0.75rem;
    height: 3rem;
    gap: 0.5rem;
  }

  .topnav-item {
    padding: 0.4375rem 0.625rem;
    font-size: 0.75rem;
  }

  .study-pill {
    padding: 0.1875rem 0.4375rem 0.1875rem 0.1875rem;
    height: 2rem;
  }

  .study-pill__icon {
    width: 1.5rem;
    height: 1.5rem;
  }

  .study-pill__time {
    font-size: 0.75rem;
  }

  .study-pill__unit {
    display: none;
  }

  .study-pill__progress {
    width: 40px;
  }

  .study-pill__btn {
    width: 1.25rem;
    height: 1.25rem;
  }
}

/* 中等屏：开始隐藏图标，节省空间 */
@media (min-width: 641px) and (max-width: 1023px) {
  .study-pill__progress {
    width: 50px;
  }
}
</style>
