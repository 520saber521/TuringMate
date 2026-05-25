<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Settings, Bell, User, Menu } from 'lucide-vue-next'
import Avatar from '@/components/ui/Avatar.vue'

const route = useRoute()

const emit = defineEmits<{
  toggleSidebar: []
}>()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    '/': 'TuringMate',
    '/chat': 'AI 对话',
    '/photo-search': '拍照搜题',
    '/correction': '手写批改',
    '/diagnosis': '薄弱点诊断',
    '/visualize': '代码实战',
  }
  const path = route.path.startsWith('/chat') ? '/chat' : route.path
  return map[path] || 'TuringMate'
})
</script>

<template>
  <header
    class="app-header fixed top-0 left-0 right-0 z-50 h-[4.5rem] flex items-center justify-between px-4 lg:px-6"
  >
    <!-- Left: Logo + Page Title -->
    <div class="flex items-center gap-3">
      <!-- Mobile Menu Button -->
      <button
        class="w-9 h-9 rounded-xl hover:bg-primary-50 flex items-center justify-center transition-all duration-200 lg:hidden active:scale-95"
        @click="emit('toggleSidebar')"
      >
        <Menu :size="19" class="text-text-secondary" />
      </button>

      <!-- Logo -->
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-md shadow-primary-300/30">
          <span class="text-white font-bold text-sm tracking-tight">TM</span>
        </div>
        <span class="text-lg font-semibold hidden sm:block text-text-primary tracking-tight">
          TuringMate
        </span>
      </div>

      <!-- Divider -->
      <div class="hidden md:block w-px h-5 bg-primary-100 mx-1.5"></div>

      <!-- Page Title -->
      <h1 class="text-base font-medium hidden md:block text-text-secondary tracking-tight">
        {{ pageTitle }}
      </h1>
    </div>

    <!-- Right: Actions -->
    <div class="flex items-center gap-1">
      <!-- Bell -->
      <button class="w-10 h-10 rounded-xl hover:bg-primary-50/80 flex items-center justify-center transition-all duration-200 active:scale-95 relative">
        <Bell :size="19" class="text-text-secondary" />
        <span class="absolute top-2 right-2 w-2 h-2 bg-danger-500 rounded-full ring-2 ring-white"></span>
      </button>

      <!-- Settings -->
      <button class="w-10 h-10 rounded-xl hover:bg-primary-50/80 flex items-center justify-center transition-all duration-200 active:scale-95">
        <Settings :size="19" class="text-text-secondary" />
      </button>

      <!-- User Avatar -->
      <Avatar size="sm" name="用户" class="ml-1 cursor-pointer active:scale-95 transition-transform" />
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 1px 3px rgba(108, 92, 231, 0.04);
}
</style>
