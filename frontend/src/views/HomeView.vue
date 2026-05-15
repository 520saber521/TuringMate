<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  Camera,
  PenTool,
  BarChart3,
  Code2,
  TrendingUp,
  Target,
  Flame,
  ChevronRight,
  BookOpen,
  MessageCircle,
} from 'lucide-vue-next'

const router = useRouter()

const quickActions = [
  {
    key: 'chat',
    label: '引导对话',
    desc: '苏格拉底式教学',
    icon: MessageCircle,
    path: '/chat/demo',
    gradient: 'from-purple-500 to-violet-500',
    bgColor: 'bg-purple-50/60',
    iconColor: '#6C5CE7',
  },
  {
    key: 'photo',
    label: '拍照搜题',
    desc: '拍题目自动识别',
    icon: Camera,
    path: '/photo-search',
    gradient: 'from-blue-500 to-indigo-500',
    bgColor: 'bg-blue-50/60',
    iconColor: '#3B82F6',
  },
  {
    key: 'correction',
    label: '手写批改',
    desc: '定位错误步骤',
    icon: PenTool,
    path: '/correction',
    gradient: 'from-emerald-500 to-teal-500',
    bgColor: 'bg-emerald-50/60',
    iconColor: '#10B981',
  },
  {
    key: 'diagnosis',
    label: '薄弱点诊断',
    desc: '分析知识弱点',
    icon: BarChart3,
    path: '/diagnosis',
    gradient: 'from-amber-500 to-orange-500',
    bgColor: 'bg-amber-50/60',
    iconColor: '#F59E0B',
  },
  {
    key: 'visualize',
    label: '代码可视化',
    desc: '算法执行过程',
    icon: Code2,
    path: '/visualize',
    gradient: 'from-rose-500 to-pink-500',
    bgColor: 'bg-rose-50/60',
    iconColor: '#EF4444',
  },
]

const stats = [
  { icon: Target, label: '今日练习', value: '12', unit: '道题', color: '#6C5CE7' },
  { icon: TrendingUp, label: '正确率提升', value: '+8.5', unit: '%', color: '#10B981' },
  { icon: Flame, label: '连续学习', value: '7', unit: '天', color: '#F59E0B' },
]

const recentPractices = [
  { id: '1', subject: '数据结构', title: '单链表删除指定结点', progress: 80, difficulty: 3, time: '2小时前' },
  { id: '2', subject: '计组', title: '流水线数据冒险解决', progress: 60, difficulty: 4, time: '5小时前' },
  { id: '3', subject: '操作系统', title: '进程调度算法比较', progress: 100, difficulty: 2, time: '昨天' },
  { id: '4', subject: '网络', title: 'TCP三次握手过程', progress: 40, difficulty: 3, time: '昨天' },
]

function goTo(path: string) {
  router.push(path)
}

const subjectColorMap: Record<string, string> = {
  '数据结构': '#6C5CE7',
  '计组': '#3B82F6',
  '操作系统': '#10B981',
  '网络': '#EF4444',
}
</script>

<template>
  <div class="home-view animate-fade-in-up">
    <!-- Welcome Banner -->
    <section class="mb-6">
      <div class="glass-card-static p-6 !rounded-2xl relative overflow-hidden">
        <div class="absolute -top-10 -right-10 w-32 h-32 rounded-full bg-purple-100/50"></div>
        <div class="absolute -bottom-8 -left-8 w-24 h-24 rounded-full bg-indigo-50/60"></div>

        <div class="relative z-10 flex items-center justify-between">
          <div>
            <p class="text-sm" style="color: var(--color-text-secondary)">晚上好，考研人</p>
            <h2 class="text-xl font-bold mt-1" style="color: var(--color-text-primary)">
              今天想复习哪个科目？
            </h2>
            <p class="text-xs mt-2" style="color: var(--color-text-tertiary)">
              距离考研还有 <span class="font-semibold" style="color: var(--color-primary)">218</span> 天
            </p>
          </div>
          <BookOpen :size="48" class="opacity-20 flex-shrink-0" style="color: var(--color-primary)" />
        </div>
      </div>
    </section>

    <!-- Quick Actions Grid -->
    <section class="mb-6">
      <h3 class="text-base font-semibold mb-3" style="color: var(--color-text-primary)">快捷功能</h3>
      <!-- 5 items: 2 cols on mobile, 3 cols on sm+, last item spans or centers -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <button
          v-for="action in quickActions"
          :key="action.key"
          :class="[
            'quick-card !rounded-2xl p-5 text-left transition-all duration-200 active:scale-[0.97]',
            action.bgColor
          ]"
          @click="goTo(action.path)"
        >
          <div
            :class="['w-12 h-12 rounded-xl flex items-center justify-center mb-3 bg-gradient-to-br shadow-sm', action.gradient]"
          >
            <component :is="action.icon" :size="22" class="text-white" />
          </div>
          <p class="text-sm font-semibold" style="color: var(--color-text-primary)">{{ action.label }}</p>
          <p class="text-xs mt-0.5" style="color: var(--color-text-tertiary)">{{ action.desc }}</p>
        </button>
      </div>
    </section>

    <!-- Stats Cards -->
    <section class="mb-6">
      <h3 class="text-base font-semibold mb-3" style="color: var(--color-text-primary)">今日统计</h3>
      <div class="grid grid-cols-3 gap-3">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="glass-card-static !rounded-2xl p-4 text-center"
        >
          <div
            class="w-10 h-10 rounded-xl mx-auto flex items-center justify-center mb-2"
            :style="{ background: `${stat.color}15` }"
          >
            <component :is="stat.icon" :size="20" :style="{ color: stat.color }" />
          </div>
          <p class="text-xl font-bold leading-tight" style="color: var(--color-text-primary)">
            {{ stat.value }}<span class="text-xs font-normal ml-0.5">{{ stat.unit }}</span>
          </p>
          <p class="text-xs mt-1" style="color: var(--color-text-tertiary)">{{ stat.label }}</p>
        </div>
      </div>
    </section>

    <!-- Recent Practice -->
    <section class="recent-practice pb-4 lg:pb-0">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-base font-semibold" style="color: var(--color-text-primary)">最近练习</h3>
        <button class="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg hover:bg-purple-50 transition-colors active:scale-95" style="color: var(--color-primary)">
          查看全部
          <ChevronRight :size="14" />
        </button>
      </div>

      <div class="flex gap-3 overflow-x-auto pb-2 -mx-4 px-4 scrollbar-hide">
        <div
          v-for="item in recentPractices"
          :key="item.id"
          class="glass-card-static !rounded-2xl p-4 min-w-[260px] max-w-[280px] flex-shrink-0 cursor-pointer hover:shadow-lg transition-shadow"
          @click="goTo(`/chat/${item.id}`)"
        >
          <div class="flex items-start justify-between mb-3">
            <span
              class="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium"
              :style="{
                background: `${subjectColorMap[item.subject] || '#6C5CE7'}15`,
                color: subjectColorMap[item.subject] || '#6C5CE7'
              }"
            >
              {{ item.subject }}
            </span>
            <span class="text-xs" style="color: var(--color-text-tertiary)">{{ item.time }}</span>
          </div>

          <p class="text-sm font-medium line-clamp-2 mb-3" style="color: var(--color-text-primary)">
            {{ item.title }}
          </p>

          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1">
              <div class="flex gap-0.5">
                <span
                  v-for="i in 5"
                  :key="i"
                  class="w-1.5 h-1.5 rounded-full"
                  :style="{ background: i <= item.difficulty ? '#F59E0B' : '#E5E7EB' }"
                ></span>
              </div>
              <span class="text-xs ml-1" style="color: var(--color-text-tertiary)">{{ item.difficulty }}/5</span>
            </div>
            <div class="flex items-center gap-2">
              <div class="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full gradient-primary transition-all"
                  :style="{ width: `${item.progress}%` }"
                ></div>
              </div>
              <span class="text-xs font-medium" style="color: var(--color-primary)">{{ item.progress }}%</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Static glass card - no hover translateY to prevent layout shift */
.glass-card-static {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(108, 92, 231, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(108, 92, 231, 0.08);
}

/* Quick card - subtle hover only, no vertical shift */
.quick-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(108, 92, 231, 0.08);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(108, 92, 231, 0.08);
}

.quick-card:hover {
  box-shadow: 0 12px 40px rgba(108, 92, 231, 0.15);
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
