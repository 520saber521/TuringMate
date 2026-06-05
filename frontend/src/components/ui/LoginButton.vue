<script setup lang="ts">
/**
 * LoginButton - 现代登录按钮组件
 * 
 * 特性：
 * - 现代渐变配色和精致阴影
 * - 流畅的悬停和点击动画
 * - 现代化的加载状态
 * - 完整的 ARIA 属性
 * - 响应式和暗色模式支持
 */
import { ref, computed } from 'vue'
import { LogIn, ArrowRight, Check } from 'lucide-vue-next'

interface Props {
  loading?: boolean
  disabled?: boolean
  success?: boolean
  size?: 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  showIcon?: boolean
  showArrow?: boolean
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  disabled: false,
  success: false,
  size: 'md',
  variant: 'primary',
  showIcon: true,
  showArrow: false,
  fullWidth: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const isPressed = ref(false)
const isFocused = ref(false)

// 按钮尺寸配置
const sizeConfig = computed(() => {
  const configs = {
    sm: {
      padding: 'px-3.5 py-2',
      fontSize: 'text-xs',
      iconSize: 14,
      gap: 'gap-1.5',
      radius: 'rounded-lg',
    },
    md: {
      padding: 'px-5 py-2.5',
      fontSize: 'text-sm',
      iconSize: 16,
      gap: 'gap-2',
      radius: 'rounded-xl',
    },
    lg: {
      padding: 'px-6 py-3',
      fontSize: 'text-base',
      iconSize: 18,
      gap: 'gap-2.5',
      radius: 'rounded-xl',
    },
    xl: {
      padding: 'px-8 py-4',
      fontSize: 'text-lg',
      iconSize: 20,
      gap: 'gap-3',
      radius: 'rounded-2xl',
    },
  }
  return configs[props.size]
})

// 按钮样式类
const buttonClasses = computed(() => {
  const base = [
    'login-button',
    'relative inline-flex items-center justify-center',
    sizeConfig.value.padding,
    sizeConfig.value.fontSize,
    sizeConfig.value.gap,
    sizeConfig.value.radius,
    'font-bold tracking-wide',
    'transition-all duration-300 ease-out',
    'select-none outline-none overflow-hidden',
  ]

  // 宽度
  if (props.fullWidth) {
    base.push('w-full')
  }

  // 变体样式
  if (props.variant === 'primary') {
    base.push(
      'btn-primary',
    )
  } else if (props.variant === 'secondary') {
    base.push(
      'btn-secondary',
    )
  } else if (props.variant === 'outline') {
    base.push(
      'btn-outline',
    )
  } else if (props.variant === 'ghost') {
    base.push(
      'btn-ghost',
    )
  } else if (props.variant === 'danger') {
    base.push(
      'btn-danger',
    )
  }

  // 禁用状态
  if (props.disabled || props.loading) {
    base.push('opacity-60 cursor-not-allowed pointer-events-none')
  }

  // 按下状态
  if (isPressed.value && !props.disabled && !props.loading) {
    base.push('scale-[0.97]')
  }

  // 聚焦状态
  if (isFocused.value) {
    base.push('ring-4 ring-primary-400/25 ring-offset-2')
  }

  return base
})

// ARIA 属性
const ariaAttributes = computed(() => ({
  role: 'button',
  'aria-label': props.loading ? '正在处理...' : props.success ? '操作成功' : '点击按钮',
  'aria-busy': props.loading,
  'aria-disabled': props.disabled || props.loading,
  'aria-pressed': isPressed.value,
  tabindex: props.disabled || props.loading ? -1 : 0,
}))

function handleClick(event: MouseEvent) {
  if (props.disabled || props.loading) return
  emit('click', event)
}

function handleKeydown(event: KeyboardEvent) {
  if (props.disabled || props.loading) return
  
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    const mouseEvent = new MouseEvent('click', {
      bubbles: true,
      cancelable: true,
    })
    handleClick(mouseEvent)
  }
}

function handleMousedown() {
  isPressed.value = true
}

function handleMouseup() {
  isPressed.value = false
}

function handleFocus() {
  isFocused.value = true
}

function handleBlur() {
  isFocused.value = false
}
</script>

<template>
  <button
    :class="buttonClasses"
    v-bind="ariaAttributes"
    :disabled="disabled || loading"
    @click="handleClick"
    @keydown="handleKeydown"
    @mousedown="handleMousedown"
    @mouseup="handleMouseup"
    @mouseleave="isPressed = false"
    @focus="handleFocus"
    @blur="handleBlur"
  >
    <!-- 按钮内容层 -->
    <span class="button-content relative z-10 flex items-center justify-center gap-2">
      <!-- 加载状态 -->
      <span v-if="loading" class="loading-wrapper">
        <svg class="spinner" viewBox="0 0 24 24">
          <circle 
            class="spinner-track" 
            cx="12" cy="12" r="9" 
            fill="none" 
            stroke-width="2.5"
          />
          <circle 
            class="spinner-head" 
            cx="12" cy="12" r="9" 
            fill="none" 
            stroke-width="2.5"
            stroke-linecap="round"
          />
        </svg>
      </span>

      <!-- 成功状态 -->
      <span v-else-if="success" class="success-wrapper">
        <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </span>

      <!-- 图标 -->
      <span v-else-if="showIcon" class="icon-wrapper">
        <component :is="success ? Check : LogIn" :size="sizeConfig.iconSize" />
      </span>

      <!-- 文本 -->
      <span class="text-wrapper">
        <slot>{{ success ? '成功' : loading ? '处理中...' : '确认' }}</slot>
      </span>

      <!-- 箭头 -->
      <span v-if="showArrow && !loading && !success" class="arrow-wrapper">
        <ArrowRight :size="sizeConfig.iconSize - 2" />
      </span>
    </span>

    <!-- 悬停光效 -->
    <span v-if="variant === 'primary' && !disabled && !loading" class="hover-effect"></span>
    
    <!-- 焦点光晕 -->
    <span v-if="isFocused" class="focus-ring"></span>
  </button>
</template>

<style scoped>
/* ================================
 * BUTTON BASE STYLES
 * ================================ */

.login-button {
  user-select: none;
}

/* ================================
 * PRIMARY VARIANT - 现代渐变按钮
 * ================================ */

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6B8DD6 100%);
  color: white;
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.35),
    0 1px 3px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #7c8ff5 0%, #8b5ec9 50%, #7c9fe8 100%);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.45),
    0 3px 8px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.btn-primary:active:not(:disabled) {
  background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 50%, #5f7ac2 100%);
  box-shadow: 
    0 2px 8px rgba(102, 126, 234, 0.3),
    inset 0 1px 2px rgba(0, 0, 0, 0.1);
  transform: translateY(0);
}

/* ================================
 * SECONDARY VARIANT
 * ================================ */

.btn-secondary {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  color: #4a5568;
  border: 1px solid #e2e8f0;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.02);
}

.btn-secondary:hover:not(:disabled) {
  background: linear-gradient(135deg, #ffffff 0%, #f0f2f5 100%);
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.03);
  transform: translateY(-1px);
  border-color: #cbd5e0;
}

/* ================================
 * OUTLINE VARIANT
 * ================================ */

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  box-shadow: none;
}

.btn-outline:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-color: #5a6fd8;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

/* ================================
 * GHOST VARIANT
 * ================================ */

.btn-ghost {
  background: transparent;
  color: #64748b;
  border: none;
  box-shadow: none;
}

.btn-ghost:hover:not(:disabled) {
  background: rgba(102, 126, 234, 0.08);
  color: #667eea;
}

.btn-ghost:active:not(:disabled) {
  background: rgba(102, 126, 234, 0.12);
}

/* ================================
 * DANGER VARIANT
 * ================================ */

.btn-danger {
  background: linear-gradient(135deg, #fc8181 0%, #e53e3e 50%, #c53030 100%);
  color: white;
  box-shadow: 
    0 4px 15px rgba(229, 62, 62, 0.35),
    0 1px 3px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(135deg, #feb2b2 0%, #f56565 50%, #e53e3e 100%);
  box-shadow: 
    0 8px 25px rgba(229, 62, 62, 0.45),
    0 3px 8px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

/* ================================
 * ANIMATIONS & EFFECTS
 * ================================ */

/* 悬停光效 */
.hover-effect {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.25) 50%,
    transparent 100%
  );
  transform: translateX(-100%);
  transition: transform 0.6s ease;
  pointer-events: none;
}

.btn-primary:hover .hover-effect {
  animation: shine 1.5s ease-in-out infinite;
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  50%, 100% { transform: translateX(100%); }
}

/* 焦点光晕 */
.focus-ring {
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  background: transparent;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.25);
  pointer-events: none;
  animation: pulse-ring 2s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* 加载动画 */
.spinner {
  width: 1.25em;
  height: 1.25em;
  animation: spin 1s linear infinite;
}

.spinner-track {
  stroke: rgba(255, 255, 255, 0.3);
}

.spinner-head {
  stroke: white;
  stroke-dasharray: 40 20;
  stroke-dashoffset: -15;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 成功状态 */
.success-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  width: 1.25em;
  height: 1.25em;
  animation: scale-in 0.3s ease-out;
}

@keyframes scale-in {
  0% { transform: scale(0); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

/* 图标和箭头动画 */
.icon-wrapper,
.arrow-wrapper {
  display: flex;
  align-items: center;
  transition: transform 0.3s ease;
}

.btn-primary:hover .icon-wrapper {
  animation: icon-bounce 0.5s ease;
}

.btn-primary:hover .arrow-wrapper {
  transform: translateX(4px);
}

@keyframes icon-bounce {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-2px); }
  75% { transform: translateX(2px); }
}

/* ================================
 * RESPONSIVE & ACCESSIBILITY
 * ================================ */

@media (max-width: 640px) {
  .login-button {
    /* 移动端更紧凑 */
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .btn-primary {
    background: #4c1d95;
    border: 2px solid white;
  }
  
  .btn-outline {
    border-width: 3px;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .login-button,
  .hover-effect,
  .focus-ring,
  .spinner,
  .check-icon,
  .icon-wrapper,
  .arrow-wrapper {
    animation: none;
    transition: none;
  }
}

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
  .btn-primary {
    box-shadow: 
      0 4px 20px rgba(102, 126, 234, 0.5),
      0 1px 4px rgba(0, 0, 0, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }
  
  .btn-primary:hover:not(:disabled) {
    box-shadow: 
      0 8px 30px rgba(102, 126, 234, 0.6),
      0 3px 6px rgba(0, 0, 0, 0.25);
  }
  
  .btn-secondary {
    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
    color: #e2e8f0;
    border-color: #4a5568;
  }
  
  .btn-secondary:hover:not(:disabled) {
    background: linear-gradient(135deg, #3d4a5c 0%, #2d3748 100%);
    border-color: #718096;
  }
}
</style>
