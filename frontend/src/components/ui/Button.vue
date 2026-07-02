<script setup lang="ts">
/**
 * Button — 全局统一按钮组件
 *
 * 设计理念：
 *  - 单一信息焦点：主操作只允许 1 个
 *  - 圆角统一 12px (lg) / 9999px (pill)
 *  - 三层渐变：背景 / 阴影 / 扫光
 *  - 触摸目标 ≥ 44px
 *  - 6 种变体 + 3 种尺寸 + 4 种状态
 */
import { computed } from 'vue'
import type { Component } from 'vue'
import { Loader2 } from 'lucide-vue-next'

interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  shape?: 'default' | 'pill' | 'square'
  loading?: boolean
  disabled?: boolean
  block?: boolean
  icon?: Component
  iconRight?: Component
  type?: 'button' | 'submit' | 'reset'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  shape: 'default',
  loading: false,
  disabled: false,
  block: false,
  type: 'button',
})

defineEmits<{
  (e: 'click', evt: MouseEvent): void
}>()

/** 变体配置 — 使用 CSS 设计令牌 */
const variantStyles: Record<NonNullable<Props['variant']>, string> = {
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
    'bg-transparent text-[var(--color-text-secondary)]',
    'border border-transparent',
    'hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]',
    'active:bg-[var(--color-neutral-200)]',
  ].join(' '),
  danger: [
    'bg-[var(--color-danger)] text-[var(--color-text-inverse)]',
    'border border-[var(--color-danger)]',
    'shadow-[0_1px_2px_rgba(239,68,68,0.16),0_4px_12px_-2px_rgba(239,68,68,0.32)]',
    'hover:bg-[var(--color-danger-600)] hover:border-[var(--color-danger-600)]',
    'active:bg-[var(--color-danger-700)]',
  ].join(' '),
  success: [
    'bg-[var(--color-success)] text-[var(--color-text-inverse)]',
    'border border-[var(--color-success)]',
    'shadow-[0_1px_2px_rgba(34,197,94,0.16),0_4px_12px_-2px_rgba(34,197,94,0.32)]',
    'hover:bg-[var(--color-success-600)] hover:border-[var(--color-success-600)]',
    'active:bg-[var(--color-success-700)]',
  ].join(' '),
}

/** 尺寸配置 — 高度符合 4/8px 网格 + 44px 触摸标准 */
const sizeStyles: Record<NonNullable<Props['size']>, string> = {
  sm: 'h-8 px-3 text-xs gap-1.5',   // 32px 高度
  md: 'h-11 px-4 text-sm gap-2',     // 44px 标准
  lg: 'h-12 px-6 text-base gap-2.5', // 48px 强调
}

/** 圆角配置 */
const shapeStyles: Record<NonNullable<Props['shape']>, string> = {
  default: 'rounded-xl',           // 12px
  pill: 'rounded-full',            // 9999px
  square: 'rounded-lg aspect-square px-0', // 8px 正方形
}

const buttonClasses = computed(() => {
  const base = [
    'relative inline-flex items-center justify-center',
    'font-semibold tracking-[var(--letter-spacing-wide)]',
    'select-none whitespace-nowrap',
    'transition-all duration-[var(--transition-fast)] ease-[cubic-bezier(0.4,0,0.2,1)]',
    'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    'active:scale-[0.98]',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary)]/40 focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-elevated)]',
    'overflow-hidden',
  ].join(' ')

  return [
    base,
    variantStyles[props.variant],
    sizeStyles[props.size],
    shapeStyles[props.shape],
    props.block ? 'w-full' : '',
  ].join(' ')
})

const iconSize = computed(() => {
  return props.size === 'sm' ? 14 : props.size === 'lg' ? 18 : 16
})
</script>

<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    @click="(e: MouseEvent) => $emit('click', e)"
  >
    <span
      v-if="variant === 'primary' || variant === 'danger' || variant === 'success'"
      class="btn-shine absolute inset-0 pointer-events-none opacity-0 hover:opacity-100 transition-opacity duration-[var(--transition-slow)]"
      aria-hidden="true"
    >
      <span
        class="absolute inset-0 translate-x-[-100%] hover:translate-x-[100%] transition-transform duration-700 ease-out"
        style="background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.2) 50%, transparent 100%);"
      ></span>
    </span>

    <!-- Loading Spinner -->
    <span v-if="loading" class="relative z-10 inline-flex">
      <Loader2 :size="iconSize" class="animate-spin" />
    </span>

    <!-- 左侧图标 -->
    <component
      v-else-if="icon"
      :is="icon"
      :size="iconSize"
      class="relative z-10 flex-shrink-0"
    />

    <!-- 文字内容 -->
    <span v-if="$slots.default" class="relative z-10 inline-flex items-center">
      <slot />
    </span>

    <!-- 右侧图标 -->
    <component
      v-if="iconRight && !loading"
      :is="iconRight"
      :size="iconSize"
      class="relative z-10 flex-shrink-0 transition-transform duration-200 group-hover:translate-x-0.5"
    />
  </button>
</template>

<style scoped>
/* 兼容旧 Tailwind 主题色 token（防止硬编码未命中时回退） */
button {
  font-family: inherit;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* hover 时扫光动画 */
button:hover > span > span {
  transform: translateX(100%);
}
</style>
