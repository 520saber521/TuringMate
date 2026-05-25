<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  error?: boolean
  icon?: Component
  iconRight?: Component
  type?: 'text' | 'password' | 'email' | 'number'
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '',
  disabled: false,
  error: false,
  type: 'text',
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const inputClasses = computed(() => {
  const base = 'w-full px-4 py-3 text-sm bg-white border rounded-xl transition-all duration-200 focus:outline-none'
  const errorClass = props.error ? 'border-danger-400 focus:border-danger-500 focus:ring-2 focus:ring-danger-500/20' : 'border-border focus:border-primary-400 focus:ring-2 focus:ring-primary-500/20'
  const disabledClass = props.disabled ? 'disabled:opacity-50 disabled:cursor-not-allowed' : ''
  return `${base} ${errorClass} ${disabledClass}`
})

function handleInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}
</script>

<template>
  <div class="relative">
    <component v-if="icon" :is="icon" class="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" :size="18" />
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      @input="handleInput"
    />
    <component v-if="iconRight" :is="iconRight" class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400" :size="18" />
  </div>
</template>
