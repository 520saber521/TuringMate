<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  icon?: Component
  iconRight?: Component
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
})

defineEmits<{
  click: []
}>()

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]'
  
  const variants: Record<string, string> = {
    primary: 'gradient-primary text-white shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-primary-500/30',
    secondary: 'bg-white text-text-secondary border border-border hover:bg-primary-50 hover:border-primary-200 focus:ring-primary-500/20',
    outline: 'bg-transparent text-primary border border-primary-300 hover:bg-primary-50 focus:ring-primary-500/20',
    ghost: 'bg-transparent text-text-secondary hover:bg-primary-50 focus:ring-primary-500/20',
    danger: 'bg-danger-500 text-white hover:bg-danger-600 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-danger-500/30',
    success: 'bg-success-500 text-white hover:bg-success-600 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-success-500/30',
    warning: 'bg-warning-500 text-white hover:bg-warning-600 shadow-md hover:shadow-lg hover:-translate-y-0.5 focus:ring-warning-500/30',
  }
  
  const sizes: Record<string, string> = {
    sm: 'px-3 py-1.5 text-xs rounded-lg',
    md: 'px-4 py-2 text-sm rounded-xl',
    lg: 'px-6 py-3 text-base rounded-xl',
  }
  
  return `${base} ${variants[props.variant]} ${sizes[props.size]}`
})
</script>

<template>
  <button :class="buttonClasses" :disabled="disabled || loading" @click="$emit('click')">
    <span v-if="loading" class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
    <component v-else-if="icon" :is="icon" :size="size === 'sm' ? 14 : size === 'lg' ? 20 : 16" />
    <slot />
    <component v-if="iconRight && !loading" :is="iconRight" :size="size === 'sm' ? 14 : size === 'lg' ? 20 : 16" />
  </button>
</template>
