<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { resolvedTheme, setTheme } = useTheme()

const isDark = resolvedTheme

function toggle() {
  setTheme(isDark.value === 'dark' ? 'light' : 'dark')
}
</script>

<template>
  <div class="theme-toggle" :class="{ dark: isDark === 'dark' }" @click="toggle">
    <div class="toggle-circle">
      <div class="crescent" />
    </div>
    <div class="toggle-track">
      <span class="label light-label">浅色</span>
      <span class="label dark-label">深色</span>
      <div class="toggle-thumb" />
    </div>
  </div>
</template>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* ── Circle with crescent animation ── */
.toggle-circle {
  position: relative;
  border-radius: 100%;
  width: 28px;
  height: 28px;
  background: linear-gradient(40deg, #FF0080, #FF8C00 70%);
  flex-shrink: 0;
  transition: background 0.5s ease;
}

.theme-toggle.dark .toggle-circle {
  background: linear-gradient(40deg, #8983F7, #A3DAFB 70%);
}

.crescent {
  position: absolute;
  border-radius: 100%;
  right: 0;
  width: 20px;
  height: 20px;
  background: #fff;
  transform: scale(0);
  transform-origin: top right;
  transition: transform 0.5s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.theme-toggle.dark .crescent {
  transform: scale(1);
  background: #26242E;
}

/* ── Track ── */
.toggle-track {
  position: relative;
  width: 72px;
  height: 32px;
  border-radius: 100px;
  background: rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  transition: background 0.3s ease;
}

.theme-toggle.dark .toggle-track {
  background: rgba(255, 255, 255, 0.1);
}

/* ── Labels ── */
.label {
  position: absolute;
  font-size: 11px;
  font-weight: 600;
  z-index: 1;
  transition: color 0.3s ease;
  width: 36px;
  text-align: center;
}

.light-label {
  left: 0;
  color: #333;
}

.theme-toggle.dark .light-label {
  color: rgba(255, 255, 255, 0.4);
}

.dark-label {
  right: 0;
  color: rgba(0, 0, 0, 0.4);
}

.theme-toggle.dark .dark-label {
  color: rgba(255, 255, 255, 0.9);
}

/* ── Thumb ── */
.toggle-thumb {
  position: absolute;
  width: 34px;
  height: 28px;
  left: 2px;
  border-radius: 100px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 2;
}

.theme-toggle.dark .toggle-thumb {
  transform: translateX(34px);
  background: #34323D;
}
</style>
