<script setup lang="ts">
import { ref, computed, provide } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue' // 已改造为顶部 TopNav
import BottomNav from './BottomNav.vue'

const sidebarCollapsed = ref(false)

const sidebarWidth = computed(() => (sidebarCollapsed.value ? '5rem' : '15rem'))

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

provide('sidebarCollapsed', sidebarCollapsed)
provide('toggleSidebar', toggleSidebar)
</script>

<template>
  <div class="app-layout-root" :style="{ '--sidebar-width': sidebarWidth }">
    <!-- 极简背景：单层柔光 -->
    <div class="bg-decoration" aria-hidden="true"></div>

    <!-- 顶栏：Logo + 标题 + 操作 -->
    <AppHeader @toggle-sidebar="toggleSidebar" />

    <!-- 顶部水平导航栏（原侧边栏改造） -->
    <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />

    <!-- 主内容 -->
    <main
      :class="[
        'main-content-area',
        sidebarCollapsed ? 'main--sidebar-collapsed' : 'main--sidebar-expanded'
      ]"
    >
      <div class="content-wrapper">
        <slot />
      </div>
    </main>

    <!-- 移动端底部导航 -->
    <BottomNav />
  </div>
</template>

<style scoped>
/* ============================================
   LAYOUT — 大气简约（顶部导航版）
   ============================================ */

.app-layout-root {
  position: relative;
  min-height: 100vh;
  width: 100%;
  background: #fafbfc;
}

/* 极简背景：单层青绿柔光 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 60% 50% at 100% 0%, rgba(13, 148, 136, 0.04) 0%, transparent 60%),
    radial-gradient(ellipse 40% 40% at 0% 100%, rgba(20, 184, 166, 0.025) 0%, transparent 55%);
}

/* 主内容区
   ── 顶栏 4.5rem + 顶部导航 3.25rem = 7.75rem ── */
.main-content-area {
  position: relative;
  z-index: 1;
  flex: 1;
  width: 100%;
  display: flex;
  justify-content: flex-start;
  padding-top: 7.75rem;
  transition: padding 0.3s ease;
}

/* 桌面端 */
@media (min-width: 1024px) {
  .main-content-area {
    min-height: 100vh;
    padding-bottom: 2rem;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

/* 平板 */
@media (min-width: 768px) and (max-width: 1023px) {
  .main-content-area {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
    padding-bottom: 2rem;
  }
}

/* 移动端 */
@media (max-width: 767px) {
  .main-content-area {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 7.5rem; /* 顶栏 4.5rem + 顶部导航 3rem */
    padding-bottom: 5rem; /* 留出 bottom nav 空间 */
  }
}

/* 内容容器 */
.content-wrapper {
  width: 100%;
  max-width: 100%;
  padding: 1.25rem;
  animation: fadeIn 0.3s ease;
}

@media (min-width: 768px) {
  .content-wrapper {
    padding: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .content-wrapper {
    padding: 2rem 2.5rem;
  }
}

@media (min-width: 1280px) {
  .content-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2.5rem 3rem;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
