<script setup lang="ts">
import { ref, computed, provide } from 'vue'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import BottomNav from './BottomNav.vue'

const sidebarCollapsed = ref(false)

const sidebarWidth = computed(() => (sidebarCollapsed ? '5rem' : '15rem'))

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

provide('sidebarCollapsed', sidebarCollapsed)
provide('toggleSidebar', toggleSidebar)
</script>

<template>
  <div class="app-layout-root" :style="{ '--sidebar-width': sidebarWidth }">
    <!-- Decorative Background -->
    <div class="bg-decoration" aria-hidden="true">
      <div class="bg-blob bg-blob--top-left"></div>
      <div class="bg-blob bg-blob--bottom-right"></div>
      <div class="bg-blob bg-blob--center"></div>
    </div>

    <!-- Top Header (fixed, full-width) -->
    <AppHeader @toggle-sidebar="toggleSidebar" />

    <!-- Desktop Sidebar -->
    <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />

    <!-- Main Content Area -->
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

    <!-- Bottom Navigation (mobile only) -->
    <BottomNav />
  </div>
</template>

<style scoped>
/* ============================================
 * ROOT LAYOUT - 全局居中布局
 * ============================================ */

.app-layout-root {
  position: relative;
  min-height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  background:
    radial-gradient(ellipse 70% 50% at 50% 0%, var(--bg-blob-1, rgba(245, 158, 11, 0.05)) 0%, transparent 60%),
    radial-gradient(ellipse 40% 45% at 10% 65%, var(--bg-blob-2, rgba(124, 58, 237, 0.03)) 0%, transparent 55%),
    radial-gradient(ellipse 35% 30% at 92% 18%, var(--bg-blob-3, rgba(56, 189, 248, 0.025)) 0%, transparent 50%),
    var(--color-bg-page, #faf8f5);
  overflow-x: hidden;
}

/* ============================================
 * 背景装饰光斑
 * ============================================ */

.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  will-change: transform;
}

.bg-blob--top-left {
  width: 45vw;
  height: 45vw;
  max-width: 700px;
  max-height: 700px;
  top: -15%;
  left: -10%;
  background: radial-gradient(circle,
    rgba(124, 58, 237, 0.12) 0%,
    rgba(245, 158, 11, 0.08) 40%,
    transparent 70%
  );
  animation: blobDriftTL 20s ease-in-out infinite alternate;
}

.bg-blob--bottom-right {
  width: 40vw;
  height: 40vw;
  max-width: 600px;
  max-height: 600px;
  bottom: -10%;
  right: -8%;
  background: radial-gradient(circle,
    rgba(245, 158, 11, 0.1) 0%,
    rgba(255, 107, 107, 0.06) 40%,
    transparent 70%
  );
  animation: blobDriftBR 25s ease-in-out infinite alternate;
}

.bg-blob--center {
  width: 30vw;
  height: 30vw;
  max-width: 450px;
  max-height: 450px;
  top: 45%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle,
    rgba(245, 158, 11, 0.07) 0%,
    rgba(124, 58, 237, 0.04) 40%,
    transparent 70%
  );
  animation: blobDriftCenter 18s ease-in-out infinite alternate;
}

@keyframes blobDriftTL {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(8%, 6%) scale(1.08); }
}

@keyframes blobDriftBR {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(-6%, -8%) scale(1.06); }
}

@keyframes blobDriftCenter {
  0% { transform: translate(-50%, -50%) scale(1); }
  100% { transform: translate(-48%, -52%) scale(1.1); }
}

/* ============================================
 * 主内容区域 - 居中适配侧边栏
 * ============================================ */

.main-content-area {
  position: relative;
  z-index: 1;
  flex: 1;
  width: 100%;
  display: flex;
  justify-content: center;
  padding-top: 4.5rem;        /* h-16 + extra breathing room */
  padding-bottom: 5.5rem;     /* bottom nav space for mobile */
  transition: padding-left var(--transition-normal);
}

/* 桌面端：侧边栏展开时补偿偏移 */
@media (min-width: 1024px) {
  .main-content-area {
    padding-bottom: 2rem;
    min-height: 100vh;
  }

  .main--sidebar-expanded {
    padding-left: 15rem;
  }

  .main--sidebar-collapsed {
    padding-left: 5rem;
  }
}

/* 移动端 */
@media (max-width: 1023px) {
  .main-content-area {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-bottom: calc(5rem + env(safe-area-inset-bottom, 0px));
  }
}

/* ============================================
 * 内容包裹器 - 真正的内容居中
 * ============================================ */

.content-wrapper {
  width: 100%;
  max-width: 1080px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1.25rem;
  padding-right: 1.25rem;
}

@media (min-width: 768px) {
  .content-wrapper {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

@media (min-width: 1280px) {
  .content-wrapper {
    max-width: 1120px;
    padding-left: 2rem;
    padding-right: 2rem;
  }
}

/* 窄屏侧边栏展开时，内容区域不宜过宽 */
@media (min-width: 1024px) and (max-width: 1279px) {
  .main--sidebar-expanded .content-wrapper {
    max-width: 760px;
  }
}
</style>
