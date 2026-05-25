<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  value: number
  max?: number
  variant?: 'primary' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  max: 100,
  variant: 'primary',
  size: 'md',
  showLabel: false,
})

const percentage = computed(() => {
  return Math.min((props.value / props.max) * 100, 100)
})

const barColor = computed(() => {
  const colors: Record<string, string> = {
    primary: 'linear-gradient(90deg, var(--color-primary-400), var(--color-primary-600))',
    success: 'linear-gradient(90deg, var(--color-success-400), var(--color-success-600))',
    warning: 'linear-gradient(90deg, var(--color-warning-400), var(--color-warning-600))',
    danger: 'linear-gradient(90deg, var(--color-danger-400), var(--color-danger-600))',
  }
  return colors[props.variant]
})

const heightClass = computed(() => {
  const heights: Record<string, string> = {
    sm: 'h-1',
    md: 'h-1.5',
    lg: 'h-2',
  }
  return heights[props.size]
})
</script>

<template>
  <div class="flex items-center gap-3">
    <div :class="['flex-1', heightClass]" class="bg-neutral-100 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-500 ease-out"
        :style="{ width: `${percentage}%`, background: barColor }"
      ></div>
    </div>
    <span v-if="showLabel" class="text-xs font-medium text-text-secondary min-w-[40px] text-right">
      {{ Math.round(percentage) }}%
    </span>
  </div>
</template>
