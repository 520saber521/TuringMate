<script setup lang="ts">
import { computed } from 'vue'
import { User } from 'lucide-vue-next'

interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  name?: string
  color?: string
  image?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  name: '',
  color: '#6C5CE7',
})

const sizeClasses = computed(() => {
  const sizes: Record<string, string> = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  }
  return sizes[props.size]
})

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name.charAt(0).toUpperCase()
})
</script>

<template>
  <div
    :class="[sizeClasses, 'rounded-full flex items-center justify-center font-semibold text-white flex-shrink-0']"
    :style="{ background: image ? 'transparent' : `linear-gradient(135deg, ${color}, ${color}99)` }"
  >
    <img v-if="image" :src="image" :alt="name" class="w-full h-full rounded-full object-cover" />
    <User v-else-if="!name" :size="size === 'sm' ? 14 : size === 'lg' ? 24 : size === 'xl' ? 28 : 18" />
    <span v-else>{{ initials }}</span>
  </div>
</template>
