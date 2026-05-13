<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import BottomNav from './BottomNav.vue'
</script>

<template>
  <div class="app-layout min-h-screen" style="background: var(--color-bg-primary)">
    <!-- Top Header -->
    <AppHeader />

    <!-- Sidebar (Desktop) -->
    <AppSidebar />

    <!-- Main Content Area -->
    <main
      class="main-content pt-16 pb-20 lg:pb-4 transition-all duration-300"
      :class="{ 'lg:ml-60': true }"
    >
      <div class="content-wrapper p-4 lg:p-6 max-w-7xl mx-auto">
        <slot />
      </div>
    </main>

    <!-- Bottom Navigation (Mobile) -->
    <BottomNav />
  </div>
</template>

<style scoped>
.main-content {
  min-height: 100vh;
}
</style>
