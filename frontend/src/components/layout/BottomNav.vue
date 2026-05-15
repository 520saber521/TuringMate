<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Camera,
  MessageCircle,
  PenTool,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/chat/demo', icon: MessageCircle, label: '对话' },
  { path: '/photo-search', icon: Camera, label: '搜题' },
  { path: '/correction', icon: PenTool, label: '批改' },
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
  <nav class="bottom-nav fixed bottom-0 left-0 right-0 z-50 lg:hidden">
    <div class="nav-inner flex items-center justify-around py-1 px-2 safe-area-bottom">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-tab flex flex-col items-center gap-0.5 py-1.5 px-4 rounded-2xl transition-all duration-200 min-w-[60px] active:scale-95',
          activePath === item.path ? 'is-active' : ''
        ]"
        @click="navigate(item.path)"
      >
        <div
          :class="[
            'w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-200',
            activePath === item.path
              ? 'gradient-primary shadow-lg shadow-purple-300/40 scale-105'
              : 'bg-transparent'
          ]"
        >
          <component
            :is="item.icon"
            :size="20"
            :class="['transition-colors duration-200', activePath === item.path ? 'text-white' : '']"
            :style="{ color: activePath === item.path ? undefined : 'var(--color-text-tertiary)' }"
          />
        </div>
        <span
          :class="[
            'text-[11px] font-medium leading-tight transition-colors duration-200',
          ]"
          :style="{ color: activePath === item.path ? 'var(--color-primary)' : 'var(--color-text-tertiary)' }"
        >
          {{ item.label }}
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
.nav-inner {
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(108, 92, 231, 0.06);
}

.safe-area-bottom {
  padding-bottom: max(6px, env(safe-area-inset-bottom));
}

/* Active tab subtle background glow */
.nav-tab.is-active {
  background: rgba(108, 92, 231, 0.04);
}
</style>
