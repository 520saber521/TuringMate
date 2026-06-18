<script setup lang="ts">
/**
 * LoginButton — 登录按钮（复用项目 Button 设计体系）
 *
 * 与 Button.vue 统一：
 *  - 相同的设计令牌（--color-primary / --shadow-* / --transition-fast）
 *  - 相同的字重/间距/过渡曲线
 *  - 相同的圆角/尺寸规范
 *
 * 额外能力：状态文字切换、右侧箭头、成功态
 */
import { computed } from 'vue'
import { ArrowRight, Loader2, Check } from 'lucide-vue-next'

interface Props {
  loading?: boolean
  disabled?: boolean
  success?: boolean
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  shape?: 'default' | 'pill' | 'square'
  fullWidth?: boolean
  showArrow?: boolean
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  success: false,
  variant: 'primary',
  size: 'md',
  shape: 'default',
  fullWidth: false,
  showArrow: true,
  label: '立即登录',
})

const emit = defineEmits<{
  (e: 'click', evt: MouseEvent): void
}>()

/* ───── 尺寸（对齐 Button.vue） ───── */
const sizeMap: Record<NonNullable<Props['size']>, { h: string; pad: string; text: string; icon: number; gap: string }> = {
  sm:   { h: 'h-8',    pad: 'px-3',  text: 'text-xs',   icon: 14, gap: 'gap-1.5' },
  md:   { h: 'h-11',   pad: 'px-4',  text: 'text-sm',   icon: 16, gap: 'gap-2' },
  lg:   { h: 'h-12',  pad: 'px-6',  text: 'text-base', icon: 18, gap: 'gap-2.5' },
  xl:   { h: 'h-14',  pad: 'px-8',  text: 'text-lg',   icon: 20, gap: 'gap-3' },
}

/* ───── 圆角（对齐 Button.vue） ───── */
const shapeMap: Record<NonNullable<Props['shape']>, string> = {
  default: 'rounded-xl',
  pill:    'rounded-full',
  square:  'rounded-lg aspect-square px-0',
}

/* ───── 变体（完全复用 Button.vue 的设计令牌） ───── */
const variantMap: Record<NonNullable<Props['variant']>, string> = {
  primary: [
    'bg-[var(--color-primary)] text-[var(--color-text-inverse)]',
    'border border-[var(--color-primary)]',
    'shadow-[var(--shadow-md)]',
    'hover:bg-[var(--color-primary-dark)] hover:border-[var(--color-primary-dark)] hover:shadow-[var(--shadow-lg)]',
    'active:bg-[var(--color-primary-800)] active:shadow-[var(--shadow-sm)]',
  ].join(' '),
  secondary: [
    'bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)]',
    'border border-[var(--color-border)]',
    'shadow-[var(--shadow-xs)]',
    'hover:bg-[var(--color-bg-subtle)] hover:border-[var(--color-border-strong)] hover:shadow-[var(--shadow-sm)]',
    'active:bg-[var(--color-neutral-100)] active:shadow-none',
  ].join(' '),
  outline: [
    'bg-transparent text-[var(--color-primary)]',
    'border border-[var(--color-primary)]/40',
    'hover:bg-[var(--color-primary)]/[0.04] hover:border-[var(--color-primary)]/60',
    'active:bg-[var(--color-primary)]/[0.08]',
  ].join(' '),
  ghost: [
    'bg-transparent text-[var(--color-text-secondary)] border border-transparent',
    'hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]',
    'active:bg-[var(--color-neutral-200)]',
  ].join(' '),
}

const displayLabel = computed(() => {
  if (props.loading) return '登录中...'
  if (props.success) return '登录成功'
  return props.label
})

function onClick(e: MouseEvent) {
  if (props.disabled || props.loading) return
  emit('click', e)
}
</script>

<template>
  <button
    type="button"
    :class="[
      'relative inline-flex items-center justify-center',
      'font-semibold tracking-[var(--letter-spacing-wide)]',
      'select-none whitespace-nowrap overflow-hidden',
      'transition-all duration-[var(--transition-fast)] ease-[cubic-bezier(0.4,0,0.2,1)]',
      sizeMap[size].h,
      sizeMap[size].pad,
      sizeMap[size].text,
      sizeMap[size].gap,
      shapeMap[shape],
      variantMap[variant],
      fullWidth ? 'w-full' : '',
      (disabled || loading) ? 'opacity-50 cursor-not-allowed pointer-events-none' : '',
      'active:scale-[0.98]',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]/40 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-elevated)]',
    ]"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    @click="onClick"
  >
    <!-- Loading Spinner -->
    <span v-if="loading" class="relative z-10 inline-flex">
      <Loader2 :size="sizeMap[size].icon" class="animate-spin" />
    </span>

    <!-- Success Check -->
    <span v-else-if="success" class="relative z-10 inline-flex">
      <Check :size="sizeMap[size].icon" :stroke-width="2.5" />
    </span>

    <!-- 文字 -->
    <span class="relative z-10 inline-flex items-center">
      <slot>{{ displayLabel }}</slot>
    </span>

    <!-- 右侧箭头 -->
    <span
      v-if="showArrow && !loading && !success"
      class="relative z-10 inline-flex transition-transform duration-200 group-hover:translate-x-0.5"
    >
      <ArrowRight :size="sizeMap[size].icon" />
    </span>
  </button>
</template>
