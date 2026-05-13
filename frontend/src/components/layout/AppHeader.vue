<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Settings, Bell, User } from 'lucide-vue-next'

const route = useRoute()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': '首页',
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
  <header class="app-header glass fixed top-0 left-0 right-0 z-50 h-16 flex items-center justify-between px-4 lg:px-6">
    <!-- Left: Logo + Page Title -->
    <div class="flex items-center gap-3">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
          <span class="text-white font-bold text-sm">TM</span>
        </div>
        <span class="text-lg font-semibold hidden sm:block" style="color: var(--color-text-primary)">
          TuringMate
        </span>
      </div>
      <div class="hidden md:block w-px h-6 bg-gray-200 mx-1"></div>
      <h1 class="text-base font-medium hidden md:block" style="color: var(--color-text-secondary)">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-2">
      <!-- Notifications -->
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors">
        <Bell :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <!-- Settings -->
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors">
        <Settings :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <!-- Avatar -->
      <button class="w-9 h-9 rounded-full gradient-primary flex items-center justify-center ml-1">
        <User :size="18" class="text-white" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  border-bottom: 1px solid rgba(108, 92, 231, 0.06);
}
</style>
