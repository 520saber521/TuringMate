<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  hoverable?: boolean
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  padding?: 'none' | 'sm' | 'md' | 'lg'
  /** Surface variant: paper (default) | glow (amber highlight) | ink (dark panel) */
  surface?: 'paper' | 'glow' | 'ink'
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  shadow: 'md',
  padding: 'md',
  surface: 'paper',
})

const cardClasses = computed(() => {
  const surfaces: Record<string, string> = {
    paper: 'surface-paper',
    glow: 'surface-glow',
    ink: 'surface-ink',
  }

  const shadows: Record<string, string> = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
  }

  const paddings: Record<string, string> = {
    none: '',
    sm: 'p-3',
    md: 'p-4',
    lg: 'p-6',
  }

  const hover = props.hoverable
    ? 'hover:-translate-y-0.5 cursor-pointer'
    : ''

  return `${surfaces[props.surface]} ${shadows[props.shadow]} ${paddings[props.padding]} ${hover}`
})
</script>

<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>
