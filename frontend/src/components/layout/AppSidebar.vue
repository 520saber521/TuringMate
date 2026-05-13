<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Camera,
  PenTool,
  BarChart3,
  Code2,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页', color: '#6C5CE7' },
  { path: '/photo-search', icon: Camera, label: '拍照搜题', color: '#3B82F6' },
  { path: '/correction', icon: PenTool, label: '手写批改', color: '#10B981' },
  { path: '/diagnosis', icon: BarChart3, label: '薄弱点诊断', color: '#F59E0B' },
  { path: '/visualize', icon: Code2, label: '代码可视化', color: '#EF4444' },
]

const activePath = computed(() => {
  if (route.path.startsWith('/chat')) return '/photo-search'
  return route.path
})

function navigate(path: string) {
  router.push(path)
}
</script>

<template>
  <aside class="sidebar glass fixed left-0 top-16 bottom-0 w-60 flex flex-col py-4 z-40 hidden lg:flex">
    <!-- Nav Items -->
    <nav class="flex-1 px-3 space-y-1">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-item w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200',
          activePath === item.path
            ? 'active'
            : 'hover:bg-purple-50/50'
        ]"
        @click="navigate(item.path)"
      >
        <component
          :is="item.icon"
          :size="20"
          :style="{ color: activePath === item.path ? item.color : 'var(--color-text-tertiary)' }"
        />
        <span>{{ item.label }}</span>
        <div
          v-if="activePath === item.path"
          class="ml-auto w-1.5 h-1.5 rounded-full"
          :style="{ background: item.color }"
        ></div>
      </button>
    </nav>

    <!-- Bottom Section -->
    <div class="px-4 pt-4 border-t border-gray-100">
      <div class="glass-card p-4 !shadow-none !rounded-xl">
        <p class="text-xs font-medium" style="color: var(--color-text-secondary)">今日学习</p>
        <p class="text-2xl font-bold gradient-text mt-1">42<span class="text-sm font-normal ml-1" style="color: var(--color-text-tertiary)">分钟</span></p>
        <div class="w-full h-1.5 bg-purple-50 rounded-full mt-3 overflow-hidden">
          <div class="h-full rounded-full gradient-primary" style="width: 65%"></div>
        </div>
        <p class="text-xs mt-1.5" style="color: var(--color-text-tertiary)">目标：每日 64 分钟</p>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  border-right: 1px solid rgba(108, 92, 231, 0.06);
}

.nav-item {
  color: var(--color-text-secondary);
}

.nav-item.active {
  background: rgba(108, 92, 231, 0.06);
  color: var(--color-primary);
}
</style>
