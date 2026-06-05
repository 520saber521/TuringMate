<script setup lang="ts">
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
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Flame,
  Play,
  Pause,
  Settings,
  Brain,
  PanelLeftClose,
  PanelLeft,
  Zap,
} from 'lucide-vue-next'
import Progress from '@/components/ui/Progress.vue'
import { useStudyTimerStore } from '@/stores/studyTimer'

interface Props {
  collapsed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  collapsed: false,
})

const emit = defineEmits<{
  toggle: []
}>()

const route = useRoute()
const router = useRouter()
const timer = useStudyTimerStore()

const editingGoal = ref(false)
const goalInputValue = ref(timer.goalMinutes)

function startEditGoal() {
  goalInputValue.value = timer.goalMinutes
  editingGoal.value = true
}

function confirmGoal() {
  const n = Number(goalInputValue.value)
  if (n >= 10 && n <= 480) {
    timer.setGoal(n)
  }
  editingGoal.value = false
}

function cancelGoal() {
  editingGoal.value = false
}

const navItems = [
  { path: '/', icon: Home, label: '首页', color: '#7c3aed', desc: '返回主页' },
  { path: '/chat/ask', icon: MessageCircle, label: 'AI 对话', color: '#8b5cf6', desc: '智能问答' },
  { path: '/camera', icon: Camera, label: '拍照识别', color: '#0ea5e9', desc: '拍照搜题' },
  { path: '/visualize', icon: Code2, label: '代码实战', color: '#ec4899', desc: '在线编程' },
  { path: '/problem-gen', icon: Sparkles, label: '举一反三', color: '#a855f7', desc: '智能出题' },
  { path: '/buddy', icon: Users, label: 'AI 研友', color: '#f59e0b', desc: '学习伙伴' },
  { path: '/diagnosis', icon: BarChart3, label: '薄弱诊断', color: '#ef4444', desc: '精准分析' },
  { path: '/mistake-book', icon: BookOpen, label: '错题本', color: '#14b8a6', desc: '查漏补缺' },
  { path: '/learning-path', icon: Route, label: '学习路径', color: '#22c55e', desc: '规划路线' },
  { path: '/thinking', icon: Brain, label: '思维回放', color: '#6366f1', desc: '思路还原' },
]

const activePath = computed(() => {
  if (route.path.startsWith('/chat')) return '/chat/ask'
  return route.path
})

function navigate(path: string) {
  if (route.path === path) return
  router.push(path)
}
</script>

<template>
  <aside
    :class="[
      'sidebar fixed left-0 top-[4.5rem] bottom-0 z-30 hidden lg:flex flex-col transition-all duration-300',
      collapsed ? 'w-20' : 'w-64',
    ]"
  >
    <!-- Top: Collapse Toggle (按主流设计放在顶部) -->
    <div class="px-3 pt-3 pb-2 flex-shrink-0">
      <button
        class="collapse-btn w-full flex items-center justify-between px-3 py-2.5 rounded-xl transition-all duration-300 group"
        :aria-label="collapsed ? '展开侧边栏' : '收起侧边栏'"
        @click="emit('toggle')"
      >
        <div class="flex items-center gap-2">
          <div class="collapse-icon-wrap">
            <component
              :is="collapsed ? PanelLeft : PanelLeftClose"
              :size="18"
              class="collapse-icon"
            />
          </div>
          <span 
            v-if="!collapsed"
            class="collapse-text text-sm font-medium"
          >
            收起侧边栏
          </span>
        </div>
        <component
          v-if="!collapsed"
          :is="ChevronLeft"
          :size="16"
          class="collapse-arrow"
        />
      </button>
    </div>

    <!-- Nav Items -->
    <nav class="flex-1 px-3 py-2 space-y-1 overflow-y-auto scrollbar-hide">
      <button
        v-for="(item, index) in navItems"
        :key="item.path"
        :class="[
          'nav-item group relative flex items-center gap-3 px-3 py-3 rounded-2xl text-sm font-medium transition-all duration-300 ease-out',
          activePath === item.path
            ? 'is-active'
            : 'hover:bg-white/70 text-text-secondary'
        ]"
        @click="navigate(item.path)"
      >
        <!-- Active indicator bar -->
        <div
          v-if="activePath === item.path"
          class="active-indicator absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 rounded-r-full transition-all duration-300"
          :style="{ background: item.color }"
        ></div>

        <!-- Icon -->
        <div
          :class="[
            'nav-icon-wrapper relative flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300',
            activePath === item.path
              ? 'shadow-lg shadow-current/15'
              : 'group-hover:scale-110 group-hover:shadow-md'
          ]"
          :style="{ 
            background: activePath === item.path ? `${item.color}18` : 'rgba(255,255,255,0.6)',
            color: activePath === item.path ? item.color : '#9ca3af'
          }"
        >
          <component
            :is="item.icon"
            :size="20"
            class="transition-transform duration-300"
            :class="activePath === item.path ? '' : 'group-hover:rotate-6'"
          />
          
          <!-- Hover glow effect -->
          <div 
            v-if="activePath !== item.path"
            class="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            :style="{ background: `${item.color}08` }"
          ></div>
        </div>

        <!-- Label & Description -->
        <transition name="fade-slide">
          <div v-if="!collapsed" class="flex-1 min-w-0 text-left">
            <div 
              class="nav-label font-semibold transition-colors duration-200"
              :style="{ color: activePath === item.path ? item.color : '#374151' }"
            >
              {{ item.label }}
            </div>
            <div class="nav-desc text-xs text-text-tertiary truncate">
              {{ item.desc }}
            </div>
          </div>
        </transition>
        
        <!-- Active indicator dot (collapsed mode) -->
        <div 
          v-if="collapsed && activePath === item.path"
          class="absolute bottom-1 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full"
          :style="{ background: item.color }"
        ></div>
      </button>
    </nav>

    <!-- Bottom Section — 今日学习 -->
    <div class="px-3 pt-3 pb-4 border-t border-slate-200/60 flex-shrink-0">
      <!-- Study Stats (Expanded) -->
      <div
        v-if="!collapsed"
        class="stats-card rounded-2xl p-5"
      >
        <!-- Header row -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <div class="stats-card__flame-wrap" :class="{ active: timer.pomodoroRunning }">
              <Flame :size="16" class="stats-card__flame-icon" />
            </div>
            <span class="text-sm font-bold text-slate-700">今日学习</span>
          </div>
          <span
            class="text-[11px] px-2.5 py-1 rounded-full font-semibold transition-all duration-300"
            :class="timer.pomodoroRunning ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
          >
            {{ timer.pomodoroRunning ? timer.phaseEmoji + ' ' + timer.phaseLabel : '⏸ 已暂停' }}
          </span>
        </div>

        <!-- Big time + Ring -->
        <div class="stats-card__time-row">
          <div class="stats-card__time-block">
            <template v-if="timer.pomodoroRunning">
              <span class="stats-card__time-num stats-card__time-num--pomodoro">{{ timer.pomodoroDisplay }}</span>
            </template>
            <template v-else>
              <span class="stats-card__time-num">{{ timer.todayMinutes }}</span>
              <span class="stats-card__time-unit">分钟</span>
            </template>
          </div>

          <!-- SVG Ring -->
          <div class="stats-card__ring">
            <svg viewBox="0 0 72 72" class="stats-card__ring-svg">
              <circle cx="36" cy="36" r="31" fill="none"
                stroke="var(--color-border-light)" stroke-width="4" />
              <circle cx="36" cy="36" r="31" fill="none"
                stroke="url(#statsRingGrad)" stroke-width="4"
                stroke-linecap="round"
                :stroke-dasharray="2 * Math.PI * 31"
                :stroke-dashoffset="2 * Math.PI * 31 * (1 - timer.progressPercent / 100)"
                transform="rotate(-90 36 36)"
                class="stats-card__ring-fill" />
            </svg>
            <span class="stats-card__ring-text">
              <template v-if="timer.pomodoroRunning && timer.pomodoroPhase === 'focus'">🍅</template>
              <template v-else>{{ timer.progressPercent }}%</template>
            </span>
            <defs>
              <linearGradient id="statsRingGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="#8b5cf6" />
                <stop offset="100%" stop-color="#f59e0b" />
              </linearGradient>
            </defs>
          </div>
        </div>

        <!-- Goal line -->
        <div class="stats-card__goal-row">
          <div v-if="!editingGoal" class="stats-card__goal-display">
            <button class="stats-card__goal-btn" @click.stop="startEditGoal">
              <span>目标 {{ timer.goalMinutes }} 分钟/天</span>
              <Settings :size="11" class="stats-card__goal-gear" />
            </button>
          </div>
          <form v-else class="stats-card__goal-edit" @submit.prevent="confirmGoal">
            <input
              v-model.number="goalInputValue"
              type="number"
              min="10"
              max="480"
              step="5"
              class="stats-card__goal-input"
              @keydown.escape="cancelGoal"
              @blur="confirmGoal"
            />
            <span class="stats-card__goal-unit">分钟/天</span>
            <button type="submit" class="stats-card__goal-confirm">✓</button>
          </form>
          <span v-if="timer.isGoalReached" class="stats-card__goal-done">✓ 已达标</span>
          <span v-else class="stats-card__goal-remain">还差 {{ timer.goalMinutes - timer.todayMinutes }} 分钟</span>
        </div>

        <!-- Toggle button -->
        <button
          v-if="timer.pomodoroPhase === 'idle' || !timer.pomodoroRunning"
          class="stats-card__toggle-btn stats-card__toggle-btn--start"
          @click.stop="timer.startFocus()"
        >
          <Play :size="14" />
          <span>{{ timer.pomodoroPhase === 'idle' ? '开始专注' : '继续专注' }}</span>
        </button>
        <button
          v-else
          class="stats-card__toggle-btn stats-card__toggle-btn--pause"
          @click.stop="timer.pausePomodoro()"
        >
          <Pause :size="14" />
          <span>暂停</span>
        </button>

        <!-- Daily summary -->
        <div
          v-if="!timer.pomodoroRunning && timer.todayMinutes > 5"
          class="stats-card__summary"
        >
          <div class="stats-card__summary-item">
            <span class="stats-card__summary-val">{{ timer.todayMinutes }}分</span>
            <span class="stats-card__summary-lbl">今日学习</span>
          </div>
          <div class="stats-card__summary-divider"></div>
          <div class="stats-card__summary-item">
            <span class="stats-card__summary-val">{{ timer.focusCountToday }}个</span>
            <span class="stats-card__summary-lbl">番茄完成</span>
          </div>
          <div v-if="timer.isGoalReached" class="stats-card__summary-goal-badge">
            ✓ 今日达标
          </div>
        </div>

        <!-- Weekly mini-bars -->
        <div class="stats-card__week">
          <div class="stats-card__week-header">
            <span class="text-[11px] font-medium text-slate-400">本周</span>
            <span class="text-[11px] text-slate-400">
              总计 <strong class="text-slate-600">{{ timer.weeklyTotal }}分</strong> · 日均 <strong class="text-slate-600">{{ timer.weeklyAvg }}分</strong>
            </span>
          </div>
          <div class="stats-card__bars">
            <div
              v-for="(day, i) in timer.weeklyData"
              :key="i"
              class="stats-card__bar-col"
            >
              <div class="stats-card__bar-track">
                <div
                  class="stats-card__bar-fill"
                  :class="{ today: day.isToday, reached: day.reached }"
                  :style="{ height: `${Math.min((day.minutes / timer.goalMinutes) * 100, 100)}%` }"
                ></div>
              </div>
              <span class="stats-card__bar-label" :class="{ today: day.isToday }">{{ day.label }}</span>
            </div>
          </div>
        </div>

        <!-- Streak -->
        <div v-if="timer.streakDays > 0" class="stats-card__streak">
          <Flame :size="14" class="stats-card__streak-icon" />
          <span>连续 <strong>{{ timer.streakDays }}</strong> 天</span>
        </div>
      </div>

      <!-- Study Stats (Collapsed) -->
      <div v-else class="text-center">
        <div
          class="stats-collapsed-wrapper relative w-12 h-12 mx-auto rounded-2xl flex items-center justify-center mb-2 transition-all duration-300"
          :class="timer.isActive ? 'bg-gradient-to-br from-emerald-400 to-emerald-500 shadow-lg shadow-emerald-300/40' : 'bg-gradient-to-br from-amber-400 to-amber-500 shadow-lg shadow-amber-300/40'"
        >
          <span class="font-bold text-lg text-white">
            {{ timer.todayMinutes }}
          </span>
          <div 
            v-if="timer.isActive"
            class="absolute inset-0 rounded-2xl animate-ping bg-emerald-400 opacity-30"
          ></div>
        </div>
        <p class="text-xs font-medium text-slate-500">分钟</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
/* ============================
   SIDEBAR — Modern Glass Effect
   ============================ */
.sidebar {
  background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(248,250,252,0.9) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-right: 1px solid rgba(148, 163, 184, 0.15);
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.02);
}

/* ============================
   COLLAPSE BUTTON - 优化位置到顶部
   ============================ */
.collapse-btn {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.06) 0%, rgba(168, 85, 247, 0.03) 100%);
  border: 1px solid rgba(139, 92, 246, 0.1);
  cursor: pointer;
}

.collapse-btn:hover {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(168, 85, 247, 0.08) 100%);
  border-color: rgba(139, 92, 246, 0.2);
}

.collapse-btn:active {
  transform: scale(0.98);
}

.collapse-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(168, 85, 247, 0.08) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.collapse-btn:hover .collapse-icon-wrap {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%);
}

.collapse-icon {
  color: #8b5cf6;
  transition: all 0.3s ease;
}

.collapse-btn:hover .collapse-icon {
  color: #7c3aed;
}

.collapse-text {
  color: #6b7280;
  transition: color 0.3s ease;
}

.collapse-btn:hover .collapse-text {
  color: #4b5563;
}

.collapse-arrow {
  color: #9ca3af;
  transition: all 0.3s ease;
}

.collapse-btn:hover .collapse-arrow {
  color: #8b5cf6;
  transform: translateX(-2px);
}

/* ============================
   NAV ITEMS
   ============================ */
.nav-item {
  position: relative;
  overflow: visible;
  color: #6b7280;
}

.nav-item.is-active {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(168, 85, 247, 0.04) 100%);
  font-weight: 600;
  color: #1f2937;
}

.nav-item::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05), rgba(245, 158, 11, 0.03));
  transition: opacity 0.3s ease;
}

.nav-item:hover::before {
  opacity: 1;
}

.active-indicator {
  box-shadow: 0 0 16px currentColor, 0 0 4px currentColor;
}

.nav-icon-wrapper {
  z-index: 1;
}

.nav-label {
  font-size: 0.875rem;
  letter-spacing: -0.01em;
}

.nav-desc {
  font-size: 0.7rem;
  margin-top: 0.1rem;
  letter-spacing: 0.02em;
}

/* ============================
   STATS CARD
   ============================ */
.stats-card {
  background: linear-gradient(135deg,
    rgba(139, 92, 246, 0.08) 0%,
    rgba(245, 158, 11, 0.04) 50%,
    rgba(236, 72, 153, 0.04) 100%);
  border: 1px solid rgba(139, 92, 246, 0.12);
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 20px rgba(139, 92, 246, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.stats-card::before {
  content: '';
  position: absolute;
  top: -30px;
  right: -30px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.12), transparent 70%);
  pointer-events: none;
}

.stats-card__flame-wrap {
  width: 28px;
  height: 28px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(245, 158, 11, 0.12);
  transition: all 0.3s ease;
}

.stats-card__flame-wrap.active {
  background: rgba(245, 158, 11, 0.2);
  animation: flameGlow 1.5s ease-in-out infinite;
}

.stats-card__flame-icon {
  color: #f59e0b;
}

@keyframes flameGlow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(245, 158, 11, 0); }
}

.stats-card__time-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.stats-card__time-block {
  display: flex;
  align-items: baseline;
  gap: 0.15rem;
}

.stats-card__time-num {
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  line-height: 1;
  background: linear-gradient(135deg, #1f2937 0%, #4b5563 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-card__time-num--pomodoro {
  font-size: 1.75rem;
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stats-card__time-unit {
  font-size: 0.85rem;
  font-weight: 500;
  color: #9ca3af;
}

.stats-card__ring {
  position: relative;
  width: 60px;
  height: 60px;
  flex-shrink: 0;
}

.stats-card__ring-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.stats-card__ring-fill {
  transition: stroke-dashoffset 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.stats-card__ring-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
}

.stats-card__goal-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.72rem;
  color: #9ca3af;
  margin-bottom: 0.6rem;
  gap: 0.4rem;
}

.stats-card__goal-display {
  flex-shrink: 0;
}

.stats-card__goal-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: none;
  border: none;
  color: #9ca3af;
  font-size: 0.72rem;
  font-family: inherit;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.stats-card__goal-btn:hover {
  color: #6b7280;
  background: rgba(139, 92, 246, 0.06);
}

.stats-card__goal-gear {
  opacity: 0;
  transition: opacity 0.2s ease;
  color: #9ca3af;
}

.stats-card__goal-btn:hover .stats-card__goal-gear {
  opacity: 1;
}

.stats-card__goal-edit {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.stats-card__goal-input {
  width: 48px;
  padding: 0.25rem 0.35rem;
  border: 1.5px solid #a78bfa;
  border-radius: 8px;
  font-size: 0.75rem;
  font-family: inherit;
  font-weight: 600;
  text-align: center;
  color: #1f2937;
  background: #fff;
  outline: none;
  transition: all 0.2s ease;
}

.stats-card__goal-input:focus {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.stats-card__goal-unit {
  font-size: 0.65rem;
  color: #9ca3af;
  white-space: nowrap;
}

.stats-card__goal-confirm {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #8b5cf6, #a855f7);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.stats-card__goal-confirm:hover {
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
}

.stats-card__goal-done {
  color: #10b981;
  font-weight: 600;
  white-space: nowrap;
}

.stats-card__goal-remain {
  color: #f59e0b;
  font-weight: 500;
  white-space: nowrap;
}

.stats-card__toggle-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.55rem;
  border-radius: 12px;
  border: none;
  font-size: 0.8rem;
  font-family: inherit;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 0.75rem;
}

.stats-card__toggle-btn--start {
  background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
}

.stats-card__toggle-btn--start:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.4);
}

.stats-card__toggle-btn--pause {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.stats-card__toggle-btn--pause:hover {
  background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%);
}

.stats-card__summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 0.6rem 0.5rem;
  margin-bottom: 0.75rem;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.06) 0%, rgba(168, 85, 247, 0.03) 100%);
  border-radius: 14px;
  border: 1px solid rgba(139, 92, 246, 0.1);
  flex-wrap: wrap;
  animation: summaryIn 0.4s ease;
}

@keyframes summaryIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.stats-card__summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.1rem;
  min-width: 48px;
}

.stats-card__summary-val {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stats-card__summary-lbl {
  font-size: 0.6rem;
  color: #9ca3af;
  font-weight: 500;
}

.stats-card__summary-divider {
  width: 1px;
  height: 24px;
  background: rgba(139, 92, 246, 0.15);
  margin: 0 0.5rem;
  flex-shrink: 0;
}

.stats-card__summary-goal-badge {
  width: 100%;
  text-align: center;
  margin-top: 0.4rem;
  font-size: 0.72rem;
  font-weight: 600;
  color: #059669;
  background: rgba(5, 150, 105, 0.08);
  padding: 0.25rem 0;
  border-radius: 999px;
}

.stats-card__week {
  margin-bottom: 0.5rem;
}

.stats-card__week-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.stats-card__bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.25rem;
  height: 52px;
}

.stats-card__bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  min-width: 0;
}

.stats-card__bar-track {
  width: 100%;
  height: 36px;
  border-radius: 999px;
  background: #f1f5f9;
  position: relative;
  overflow: hidden;
}

.stats-card__bar-fill {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  border-radius: 999px;
  background: #e2e8f0;
  transition: height 0.4s ease;
  min-height: 2px;
}

.stats-card__bar-fill.today {
  background: linear-gradient(180deg, #8b5cf6, #a855f7);
}

.stats-card__bar-fill.reached {
  background: #10b981;
}

.stats-card__bar-fill.today.reached {
  background: linear-gradient(180deg, #8b5cf6, #10b981);
}

.stats-card__bar-label {
  font-size: 0.6rem;
  color: #9ca3af;
  font-weight: 500;
}

.stats-card__bar-label.today {
  color: #8b5cf6;
  font-weight: 700;
}

.stats-card__streak {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.72rem;
  color: #6b7280;
  margin-top: 0.5rem;
}

.stats-card__streak-icon {
  color: #f59e0b;
}

/* ============================
   TRANSITIONS
   ============================ */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
