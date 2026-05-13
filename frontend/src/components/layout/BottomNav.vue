<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Camera,
  PenTool,
  BarChart3,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/photo-search', icon: Camera, label: '搜题' },
  { path: '/correction', icon: PenTool, label: '批改' },
  { path: '/diagnosis', icon: BarChart3, label: '诊断' },
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
  <nav class="bottom-nav fixed bottom-0 left-0 right-0 z-50 lg:hidden">
    <div class="glass flex items-center justify-around py-2 px-2 safe-area-bottom">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'flex flex-col items-center gap-0.5 py-1 px-4 rounded-xl transition-all duration-200 min-w-[60px]',
          activePath === item.path ? 'active' : ''
        ]"
        @click="navigate(item.path)"
      >
        <div
          :class="[
            'w-10 h-10 rounded-xl flex items-center justify-center transition-all',
            activePath === item.path ? 'gradient-primary shadow-md' : ''
          ]"
        >
          <component
            :is="item.icon"
            :size="20"
            :class="[
              'transition-colors',
              activePath === item.path ? 'text-white' : ''
            ]"
            :style="{ color: activePath === item.path ? undefined : 'var(--color-text-tertiary)' }"
          />
        </div>
        <span
          :class="['text-xs font-medium', activePath === item.path ? '' : '']"
          :style="{ color: activePath === item.path ? 'var(--color-primary)' : 'var(--color-text-tertiary)' }"
        >
          {{ item.label }}
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.bottom-nav {
  border-top: 1px solid rgba(108, 92, 231, 0.06);
}

.safe-area-bottom {
  padding-bottom: max(8px, env(safe-area-inset-bottom));
}
</style>
