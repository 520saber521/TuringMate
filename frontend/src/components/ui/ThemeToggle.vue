<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { resolvedTheme, setTheme } = useTheme()

function toggle() {
  setTheme(resolvedTheme.value === 'dark' ? 'light' : 'dark')
}
</script>

<template>
  <button
    type="button"
    class="theme-toggle"
    :class="{ dark: resolvedTheme === 'dark' }"
    :aria-label="resolvedTheme === 'dark' ? '切换到浅色模式' : '切换到深色模式'"
    @click="toggle"
  >
    <span class="toggle-orb" aria-hidden="true">
      <span class="toggle-crescent" />
    </span>
    <span class="toggle-track" aria-hidden="true">
      <span class="label light-label">浅色</span>
      <span class="label dark-label">深色</span>
      <span class="toggle-thumb" />
    </span>
  </button>
</template>

<style scoped>
.theme-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.toggle-orb {
  position: relative;
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  background: linear-gradient(40deg, #ff4d4f, #ffb020 72%);
  transition: background 0.3s ease;
}

.theme-toggle.dark .toggle-orb {
  background: linear-gradient(40deg, #6366f1, #38bdf8 72%);
}

.toggle-crescent {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  transform: scale(0);
  transform-origin: top right;
  transition: transform 0.3s ease;
}

.theme-toggle.dark .toggle-crescent {
  transform: scale(1);
  background: #111827;
}

.toggle-track {
  position: relative;
  display: flex;
  align-items: center;
  width: 72px;
  height: 30px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.08);
}

.theme-toggle.dark .toggle-track {
  background: rgba(255, 255, 255, 0.12);
}

.label {
  position: absolute;
  z-index: 1;
  width: 36px;
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  color: #334155;
}

.light-label {
  left: 0;
}

.dark-label {
  right: 0;
  color: rgba(15, 23, 42, 0.48);
}

.theme-toggle.dark .light-label {
  color: rgba(255, 255, 255, 0.42);
}

.theme-toggle.dark .dark-label {
  color: rgba(255, 255, 255, 0.92);
}

.toggle-thumb {
  position: absolute;
  left: 2px;
  z-index: 2;
  width: 34px;
  height: 26px;
  border-radius: 999px;
  background: #fff;
  box-shadow: 0 4px 10px -6px rgba(15, 23, 42, 0.45);
  transition:
    transform 0.25s ease,
    background 0.25s ease;
}

.theme-toggle.dark .toggle-thumb {
  transform: translateX(34px);
  background: #1f2937;
}

@media (max-width: 900px) {
  .toggle-orb {
    display: none;
  }
}

@media (max-width: 640px) {
  .toggle-track {
    width: 58px;
  }

  .label {
    width: 29px;
    font-size: 10px;
  }

  .toggle-thumb {
    width: 27px;
  }

  .theme-toggle.dark .toggle-thumb {
    transform: translateX(29px);
  }
}
</style>
