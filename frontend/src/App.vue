<script setup lang="ts">
import { computed } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useStudyTimerStore } from '@/stores/studyTimer'

const route = useRoute()
const timer = useStudyTimerStore()

// 判断是否为登录页面（独立页面）
const isStandalonePage = computed(() => {
  return route.path === '/login'
})

// Auto-track: start timer on study pages, pause on non-study pages
import { watch } from 'vue'
watch(
  () => route.path,
  (path) => {
    timer.setCurrentRoute(path)
    if (timer.isStudyRoute(path)) {
      timer.startTracking()
    } else {
      timer.pauseTracking()
    }
  },
  { immediate: true }
)
</script>

<template>
  <!-- 登录页面使用独立全屏布局 -->
  <template v-if="isStandalonePage">
    <RouterView v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </RouterView>
  </template>
  
  <!-- 其他页面使用主布局 -->
  <template v-else>
    <AppLayout>
      <RouterView v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </AppLayout>
  </template>
</template>

<style>
#app {
  min-height: 100vh;
  display: block;
  background-color: var(--color-bg-page);
}

/* 登录页面特殊处理 */
#app:has(.auth-page) {
  background-color: transparent;
  margin: 0;
  padding: 0;
}

/* 页面切换动画 */
.page-enter-active {
  animation: pageIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.page-leave-active {
  animation: pageOut 0.2s cubic-bezier(0.4, 0, 1, 1);
}

@keyframes pageIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pageOut {
  from {
    opacity: 1;
    transform: scale(1);
  }
  to {
    opacity: 0;
    transform: scale(0.98);
  }
}
</style>
