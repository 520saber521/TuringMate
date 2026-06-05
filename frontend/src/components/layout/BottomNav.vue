<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  Search,
  MessageCircle,
  User,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/camera', icon: Search, label: '拍照' },
  { path: '/chat/demo', icon: MessageCircle, label: '问AI' },
  { path: '/diagnosis', icon: User, label: '我的' },
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
    <div class="nav-inner flex items-center justify-around h-14 py-1 px-2 safe-area-bottom">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="[
          'nav-tab flex flex-col items-center gap-0.5 py-1.5 px-4 rounded-2xl transition-all duration-200 min-w-[60px] active:scale-95',
          activePath === item.path ? 'is-active' : ''
        ]"
        :aria-label="item.label"
        @click="navigate(item.path)"
      >
        <div
          :class="[
            'nav-tab__icon-wrap w-10 h-10 rounded-2xl flex items-center justify-center transition-all duration-250',
            activePath === item.path
              ? 'nav-tab__icon-wrap--active'
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
            activePath === item.path ? 'nav-tab__label--active' : ''
          ]"
          :style="{ color: activePath === item.path ? undefined : 'var(--color-text-tertiary)' }"
        >
          {{ item.label }}
        </span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
/* ============================
   BOTTOM NAV — 暖纸表面
   ============================ */
.nav-inner {
  background: var(--bottom-nav-bg, rgba(254, 253, 251, 0.88));
  backdrop-filter: blur(20px) saturate(120%);
  -webkit-backdrop-filter: blur(20px) saturate(120%);
  border-top: 1px solid rgba(120, 115, 108, 0.08);
}

.safe-area-bottom {
  padding-bottom: max(12px, env(safe-area-inset-bottom));
}

/* Active tab background */
.nav-tab.is-active {
  background: rgba(124, 58, 237, 0.04);
}

/* Active icon — 暖紫渐变 */
.nav-tab__icon-wrap--active {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.3);
  transform: scale(1.05);
}

/* Active label */
.nav-tab__label--active {
  color: var(--color-primary, #7c3aed);
  font-weight: 600;
}
</style>
