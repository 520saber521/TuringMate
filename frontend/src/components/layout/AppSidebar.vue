<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Camera,
  PenTool,
  BarChart3,
  Code2,
  MessageCircle,
  Users,
  Route,
  Sparkles,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'
import Progress from '@/components/ui/Progress.vue'

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

const navItems = [
  { path: '/', icon: Home, label: '首页', color: '#6C5CE7' },
  { path: '/chat/demo', icon: MessageCircle, label: 'AI 对话', color: '#7C3AED' },
  { path: '/photo-search', icon: Camera, label: '拍照搜题', color: '#3B82F6' },
  { path: '/correction', icon: PenTool, label: '手写批改', color: '#10B981' },
  { path: '/visualize', icon: Code2, label: '代码实战', color: '#EF4444' },
  { path: '/diagnosis', icon: BarChart3, label: '薄弱点诊断', color: '#F59E0B' },
  { path: '/chat/demo?mode=buddy', icon: Users, label: 'AI 研友', color: '#EC4899' },
  { path: '/diagnosis', icon: Route, label: '学习路径', color: '#06B6D4' },
]

const activePath = computed(() => {
  if (route.path.startsWith('/chat')) return '/chat/demo'
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
      'sidebar fixed left-0 top-0 bottom-0 z-40 hidden lg:flex flex-col pt-[4.5rem] transition-all duration-300',
      collapsed ? 'w-20' : 'w-60',
    ]"
  >
    <!-- Nav Items -->
    <nav class="flex-1 px-2.5 py-3 space-y-0.5 overflow-y-auto scrollbar-hide">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-item group w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 relative',
          activePath === item.path
            ? 'is-active'
            : 'hover:bg-white/50 text-text-secondary'
        ]"
        @click="navigate(item.path)"
      >
        <!-- Active indicator bar -->
        <div
          v-if="activePath === item.path"
          class="active-indicator absolute left-0 top-1/2 -translate-y-1/2 w-[3px] rounded-r-full transition-all duration-300"
          :style="{
            height: collapsed ? '1.5rem' : '2rem',
            background: `linear-gradient(180deg, ${item.color}, ${item.color}88)`,
          }"
        ></div>

        <!-- Icon -->
        <div
          :class="[
            'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200',
            activePath === item.path
              ? 'shadow-sm'
              : 'group-hover:scale-105'
          ]"
          :style="{
            background: activePath === item.path ? `${item.color}12` : 'transparent',
          }"
        >
          <component
            :is="item.icon"
            :size="18"
            :style="{ color: activePath === item.path ? item.color : 'var(--color-text-tertiary)' }"
          />
        </div>

        <!-- Label -->
        <transition name="fade-slide">
          <span
            v-if="!collapsed"
            class="flex-1 text-left transition-colors duration-200"
            :style="{ color: activePath === item.path ? item.color : undefined }"
          >
            {{ item.label }}
          </span>
        </transition>
      </button>
    </nav>

    <!-- Bottom Section -->
    <div class="px-2.5 pt-3 pb-4 border-t border-primary-50/60 flex-shrink-0">
      <!-- Collapse Toggle -->
      <button
        class="w-full mb-3 p-2 rounded-lg hover:bg-white/50 flex items-center justify-center transition-all duration-200 active:scale-95"
        @click="emit('toggle')"
      >
        <component
          :is="collapsed ? ChevronRight : ChevronLeft"
          :size="18"
          class="text-text-secondary transition-transform duration-300"
        />
      </button>

      <!-- Study Stats (Expanded) -->
      <div
        v-if="!collapsed"
        class="rounded-xl p-4"
        style="background: linear-gradient(135deg, rgba(108,92,231,0.07) 0%, rgba(45,212,191,0.04) 100%)"
      >
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <Sparkles :size="14" class="text-primary" />
            <p class="text-xs font-semibold text-text-secondary">今日学习</p>
          </div>
          <span class="text-xs px-1.5 py-0.5 rounded-md bg-primary-100 text-primary font-semibold">65%</span>
        </div>
        <p class="text-2xl font-bold gradient-text mt-0.5">
          42<span class="text-sm font-medium ml-1 text-text-tertiary">分钟</span>
        </p>
        <Progress value="65" class="mt-3" />
        <p class="text-xs mt-1.5 text-text-tertiary">目标：每日 64 分钟</p>
      </div>

      <!-- Study Stats (Collapsed) -->
      <div v-else class="text-center">
        <div class="w-10 h-10 mx-auto rounded-xl bg-primary-100 flex items-center justify-center mb-1">
          <span class="text-primary font-bold text-sm">42</span>
        </div>
        <p class="text-xs text-text-tertiary">分钟</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-right: 1px solid var(--color-border);
}

.nav-item {
  position: relative;
  overflow: hidden;
}

.nav-item.is-active {
  background: rgba(108, 92, 231, 0.06);
  font-weight: 600;
}

.nav-item::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  opacity: 0;
  background: linear-gradient(135deg, rgba(108, 92, 231, 0.04), transparent);
  transition: opacity 0.3s ease;
}

.nav-item:hover::after {
  opacity: 1;
}

.active-indicator {
  box-shadow: 0 0 8px rgba(108, 92, 231, 0.15);
}

/* Transition for collapsed labels */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.2s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}
</style>
