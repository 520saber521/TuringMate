<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Home, Camera, MessageCircle, User } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/camera', icon: Camera, label: '拍照' },
  { path: '/chat/ask', icon: MessageCircle, label: '问AI' },
  { path: '/profile', icon: User, label: '我的' },
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
  <nav class="bottom-nav">
    <div class="nav-inner">
      <button
        v-for="item in navItems"
        :key="item.path"
        :class="['nav-tab', { 'is-active': activePath === item.path }]"
        :aria-label="item.label"
        @click="navigate(item.path)"
      >
        <span class="nav-tab__icon">
          <component :is="item.icon" :size="20" />
        </span>
        <span class="nav-tab__label">{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>

<style scoped>
/* ============================================
   BOTTOM NAV — 大气简约（仅移动端显示）
   ============================================ */

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 50;
  display: block;
}

@media (min-width: 1024px) {
  .bottom-nav {
    display: none;
  }
}

.nav-inner {
  display: flex;
  align-items: stretch;
  justify-content: space-around;
  height: 3.5rem;
  padding: 0 0.5rem;
  padding-bottom: env(safe-area-inset-bottom, 0px);
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(15, 23, 42, 0.06);
}

.nav-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  flex: 1;
  min-width: 0;
  padding: 0.375rem 0.5rem;
  background: transparent;
  border: none;
  font-family: inherit;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s ease;
  position: relative;
}

.nav-tab:active {
  transform: scale(0.96);
}

.nav-tab__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.nav-tab__label {
  font-size: 0.6875rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  line-height: 1;
}

.nav-tab.is-active {
  color: #0d9488;
}

.nav-tab.is-active .nav-tab__icon {
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
}

.nav-tab.is-active .nav-tab__label {
  color: #0d9488;
  font-weight: 600;
}
</style>
