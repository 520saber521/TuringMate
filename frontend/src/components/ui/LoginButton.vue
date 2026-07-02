<script setup lang="ts">
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

const iconSize = computed(() => {
  const map = { sm: 14, md: 16, lg: 18, xl: 20 }
  return map[props.size]
})

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
    class="login-btn"
    :class="[
      `login-btn--${variant}`,
      `login-btn--${size}`,
      `login-btn--${shape}`,
      {
        'login-btn--full': fullWidth,
        'is-disabled': disabled || loading,
      },
    ]"
    :disabled="disabled || loading"
    :aria-busy="loading || undefined"
    @click="onClick"
  >
    <Loader2 v-if="loading" :size="iconSize" class="login-btn__spin" />
    <Check v-else-if="success" :size="iconSize" :stroke-width="2.5" />
    <span class="login-btn__label"><slot>{{ displayLabel }}</slot></span>
    <ArrowRight v-if="showArrow && !loading && !success" :size="iconSize" />
  </button>
</template>

<style scoped>
.login-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  border: 1px solid transparent;
  font-family: inherit;
  font-weight: 700;
  line-height: 1;
  letter-spacing: 0;
  white-space: nowrap;
  cursor: pointer;
  transition:
    transform var(--transition-fast),
    box-shadow var(--transition-fast),
    background var(--transition-fast),
    border-color var(--transition-fast),
    color var(--transition-fast);
}

.login-btn--sm {
  height: 2rem;
  padding: 0 0.75rem;
  font-size: 0.75rem;
}

.login-btn--md {
  height: 2.25rem;
  padding: 0 0.9rem;
  font-size: 0.875rem;
}

.login-btn--lg {
  height: 2.75rem;
  padding: 0 1.25rem;
  font-size: 0.9375rem;
}

.login-btn--xl {
  height: 3.25rem;
  padding: 0 1.5rem;
  font-size: 1rem;
}

.login-btn--default {
  border-radius: 12px;
}

.login-btn--pill {
  border-radius: 999px;
}

.login-btn--square {
  aspect-ratio: 1;
  padding-inline: 0;
}

.login-btn--full {
  width: 100%;
}

.login-btn--primary {
  color: #fff;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  border-color: rgba(13, 148, 136, 0.2);
  box-shadow: 0 12px 24px -16px rgba(13, 148, 136, 0.9);
}

.login-btn--secondary {
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.9);
  border-color: var(--color-border);
  box-shadow: var(--shadow-xs);
}

.login-btn--outline {
  color: #0d9488;
  background: rgba(255, 255, 255, 0.65);
  border-color: rgba(13, 148, 136, 0.32);
}

.login-btn--ghost {
  color: var(--color-text-secondary);
  background: transparent;
}

.login-btn:not(.is-disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px -18px rgba(13, 148, 136, 0.95);
}

.login-btn:not(.is-disabled):active {
  transform: translateY(0) scale(0.98);
}

.login-btn.is-disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.login-btn__spin {
  animation: loginSpin 0.8s linear infinite;
}

@keyframes loginSpin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .login-btn__label {
    max-width: 4.5rem;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}
</style>
