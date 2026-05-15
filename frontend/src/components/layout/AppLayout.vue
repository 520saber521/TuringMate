<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import BottomNav from './BottomNav.vue'
</script>

<template>
  <div class="app-layout min-h-screen" style="background: var(--color-bg-primary)">
    <!-- Top Header (fixed, z-50) -->
    <AppHeader />

    <!-- Sidebar (desktop only, fixed left, z-40) -->
    <AppSidebar />

    <!-- Main Content Area -->
    <main
      class="main-content min-h-screen transition-all duration-300"
      :class="[
        'pt-[4rem] pb-[4.5rem] lg:pb-6',
        'lg:pl-[15rem]',
      ]"
    >
      <div class="content-wrapper p-4 lg:p-6 max-w-7xl mx-auto">
        <slot />
      </div>
    </main>

    <!-- Bottom Navigation (mobile only, fixed bottom, z-50) -->
    <BottomNav />
  </div>
</template>

<style scoped>
.main-content {
  position: relative;
  z-index: 1;
}
</style>
