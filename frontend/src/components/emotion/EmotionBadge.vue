<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Smile, Frown, Meh, Zap, Coffee, PartyPopper, AlertCircle } from 'lucide-vue-next'
import { getEmotionState } from '@/api/emotion'
import type { EmotionType } from '@/api/emotion'

const props = defineProps<{ sessionId: string }>()

const currentEmotion = ref<EmotionType>('neutral')
let pollTimer: ReturnType<typeof setInterval> | null = null

const emotionConfig: Record<EmotionType, { icon: any; color: string; label: string }> = {
  frustrated: { icon: Frown, color: '#ef4444', label: '有点沮丧' },
  anxious: { icon: AlertCircle, color: '#f59e0b', label: '焦虑中' },
  tired: { icon: Coffee, color: '#9ca3af', label: '疲惫' },
  bored: { icon: Meh, color: '#9ca3af', label: '无聊' },
  confident: { icon: Zap, color: '#10b981', label: '自信满满' },
  excited: { icon: PartyPopper, color: '#8b5cf6', label: '兴奋' },
  neutral: { icon: Smile, color: '#6b7280', label: '平常' },
}

async function pollEmotion() {
  if (!props.sessionId) return
  try {
    const state = await getEmotionState(props.sessionId)
    currentEmotion.value = state.current_emotion
  } catch { /* silent fail */ }
}

onMounted(() => {
  pollEmotion()
  pollTimer = setInterval(pollEmotion, 30000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const config = computed(() => emotionConfig[currentEmotion.value])
</script>

<template>
  <div v-if="sessionId" class="emotion-badge" :title="config.label">
    <component :is="config.icon" :size="16" :style="{ color: config.color }" />
    <span class="emotion-label" :style="{ color: config.color }">{{ config.label }}</span>
  </div>
</template>

<style scoped>
.emotion-badge {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid var(--color-border);
  font-size: 0.75rem;
  transition: all 0.3s;
}
.emotion-label { font-weight: 500; white-space: nowrap; }
</style>
