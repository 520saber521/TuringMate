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
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页', color: '#6C5CE7' },
  { path: '/chat/demo', icon: MessageCircle, label: '引导对话', color: '#8B5CF6' },
  { path: '/photo-search', icon: Camera, label: '拍照搜题', color: '#3B82F6' },
  { path: '/correction', icon: PenTool, label: '手写批改', color: '#10B981' },
  { path: '/diagnosis', icon: BarChart3, label: '薄弱点诊断', color: '#F59E0B' },
  { path: '/visualize', icon: Code2, label: '代码可视化', color: '#EF4444' },
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
    class="sidebar fixed left-0 top-16 bottom-0 w-60 flex flex-col z-40 hidden lg:flex"
  >
    <!-- Nav Items -->
    <nav class="flex-1 px-3 py-3 space-y-1 overflow-y-auto">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-item group w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 relative',
          activePath === item.path
            ? 'is-active'
            : 'hover:bg-purple-50/60 text-[var(--color-text-secondary)]'
        ]"
        @click="navigate(item.path)"
      >
        <!-- Active left indicator -->
        <div
          v-if="activePath === item.path"
          class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full"
          :style="{ background: item.color }"
        ></div>

        <!-- Icon container -->
        <div
          :class="[
            'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200',
            activePath === item.path ? '' : 'bg-gray-50/80 group-hover:bg-purple-50 group-hover:scale-105'
          ]"
          :style="{ background: activePath === item.path ? item.color + '12' : undefined }"
        >
          <component
            :is="item.icon"
            :size="18"
            :style="{ color: activePath === item.path ? item.color : 'var(--color-text-tertiary)' }"
          />
        </div>

        <!-- Label -->
        <span
          class="flex-1 text-left transition-colors"
          :style="{ color: activePath === item.path ? item.color : undefined }"
        >
          {{ item.label }}
        </span>
      </button>
    </nav>

    <!-- Bottom Section: Study Stats -->
    <div class="px-3 pt-3 pb-4 border-t border-purple-50/80 flex-shrink-0">
      <div class="rounded-xl p-4" style="background: linear-gradient(135deg, rgba(108,92,231,0.06) 0%, rgba(167,139,250,0.04) 100%)">
        <div class="flex items-center justify-between mb-2">
          <p class="text-xs font-medium" style="color: var(--color-text-secondary)">今日学习</p>
          <span class="text-xs px-1.5 py-0.5 rounded-md" style="background: rgba(108,92,231,0.1); color: var(--color-primary)">65%</span>
        </div>
        <p class="text-2xl font-bold gradient-text mt-0.5">
          42<span class="text-sm font-normal ml-1 font-medium" style="color: var(--color-text-tertiary)">分钟</span>
        </p>
        <div class="w-full h-1.5 bg-purple-50/80 rounded-full mt-3 overflow-hidden">
          <div class="h-full rounded-full gradient-primary transition-all duration-500" style="width: 65%"></div>
        </div>
        <p class="text-xs mt-1.5" style="color: var(--color-text-tertiary)">目标：每日 64 分钟</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  border-right: 1px solid rgba(108, 92, 231, 0.06);
}

.nav-item.is-active {
  background: rgba(108, 92, 231, 0.05);
  font-weight: 600;
}

/* Override global glass-card hover for sidebar items */
.sidebar .glass-card:hover {
  transform: none;
}
</style>
