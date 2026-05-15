<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Settings, Bell, User } from 'lucide-vue-next'

const route = useRoute()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '首页',
    '/chat': '引导对话',
    '/photo-search': '拍照搜题',
    '/correction': '手写批改',
    '/diagnosis': '薄弱点诊断',
    '/visualize': '代码可视化',
  }
  const path = route.path.startsWith('/chat') ? '/chat' : route.path
  return map[path] || 'TuringMate'
})
</script>

<template>
  <header
    class="app-header fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-4 lg:px-6"
  >
    <!-- Left: Logo + Page Title -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-md shadow-purple-200/50">
          <span class="text-white font-bold text-sm tracking-tight">TM</span>
        </div>
        <span class="text-lg font-semibold hidden sm:block" style="color: var(--color-text-primary)">
          TuringMate
        </span>
      </div>
      <div class="hidden md:block w-px h-5 bg-purple-100 mx-1"></div>
      <h1 class="text-base font-medium hidden md:block" style="color: var(--color-text-secondary)">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-1.5">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50/80 flex items-center justify-center transition-colors active:scale-95">
        <Bell :size="19" style="color: var(--color-text-secondary)" />
      </button>
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50/80 flex items-center justify-center transition-colors active:scale-95">
        <Settings :size="19" style="color: var(--color-text-secondary)" />
      </button>
      <button class="w-9 h-9 rounded-full gradient-primary flex items-center justify-center ml-1.5 shadow-md shadow-purple-200/40 active:scale-95 transition-transform">
        <User :size="16" class="text-white" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(108, 92, 231, 0.06);
}
</style>
