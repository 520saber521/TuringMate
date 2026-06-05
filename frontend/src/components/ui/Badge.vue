<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'amber'
  size?: 'sm' | 'md'
  icon?: Component
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'sm',
})

const badgeClasses = computed(() => {
  const base = 'inline-flex items-center gap-1.5 font-medium rounded-full transition-all duration-200'
  
  const variants: Record<string, string> = {
    primary: 'bg-primary-50 text-primary-600',
    success: 'bg-success-50 text-success-600',
    warning: 'bg-warning-50 text-warning-600',
    danger: 'bg-danger-50 text-danger-600',
    info: 'bg-info-50 text-info-600',
  }
  
  const sizes: Record<string, string> = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  }
  
  return `${base} ${variants[props.variant]} ${sizes[props.size]}`
})
</script>

<template>
  <span :class="badgeClasses">
    <component v-if="icon" :is="icon" :size="size === 'sm' ? 12 : 14" />
    <slot />
  </span>
</template>
