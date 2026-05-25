<script setup lang="ts">
interface Props {
  hoverable?: boolean
  shadow?: 'none' | 'sm' | 'md' | 'lg'
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  hoverable: false,
  shadow: 'md',
  padding: 'md',
})

const cardClasses = computed(() => {
  const base = 'bg-white border border-border rounded-2xl transition-all duration-200'
  
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
  
  const hoverEffects = props.hoverable ? 'hover:shadow-lg hover:-translate-y-0.5 cursor-pointer' : ''
  
  return `${base} ${shadows[props.shadow]} ${paddings[props.padding]} ${hoverEffects}`
})

import { computed } from 'vue'
</script>

<template>
  <div :class="cardClasses">
    <slot />
  </div>
</template>
