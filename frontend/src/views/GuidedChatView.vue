<script setup lang="ts">
/**
 * GuidedChatView - 苏格拉底式引导对话页面
 * 接入真实后端 API，支持普通模式和 SSE 流式模式
 */
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Lightbulb, SkipForward, Eye, Square, Send } from 'lucide-vue-next'
import { useChat } from '@/composables/useChat'

const route = useRoute()
const router = useRouter()

const props = defineProps<{ questionId?: string }>()

const {
  sessionId,
  messages,
  currentStage,
  isLoading,
  isStreaming,
  isComplete,
  error,
  startGuidedChat,
  sendUserMessage,
  stopStreaming,
  scrollToBottom,
} = useChat()

const messagesContainer = ref<HTMLElement | null>(null)
const inputText = ref('')
const useStreamMode = ref(true) // 默认使用流式

// 从路由获取 questionId
const effectiveQuestionId = route.query.questionId as string || props.questionId || 'demo'

onMounted(async () => {
  if (effectiveQuestionId) {
    await startGuidedChat(effectiveQuestionId)
    scrollToBottom(messagesContainer.value)
  }
})

// 监听消息变化，自动滚动到底部
watch(() => messages.value.length, () => {
  scrollToBottom(messagesContainer.value)
})

watch(() => {
  const lastMsg = messages.value[messages.value.length - 1]
  return lastMsg?.content?.length
}, () => {
  if (isStreaming.value) {
    scrollToBottom(messagesContainer.value)
  }
})

async function sendMessage_action() {
  if (!inputText.value.trim() || isLoading.value || isStreaming.value) return

  const text = inputText.value.trim()
  inputText.value = ''

  if (useStreamMode.value) {
    // 流式模式 - 暂时用普通模式替代，因为 SSE 需要后端配合
    await sendUserMessage(text)
  } else {
    await sendUserMessage(text)
  }

  scrollToBottom(messagesContainer.value)
}

function skipHint() {
  inputText.value = '跳过提示，请继续'
  sendMessage_action()
}

function endChat() {
  router.push('/')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage_action()
  }
}
</script>

<template>
  <div class="guided-chat-view flex flex-col animate-fade-in-up">
    <!-- Header bar -->
    <div class="flex items-center gap-3 px-2 py-3 border-b border-purple-50/80 flex-shrink-0" style="background: rgba(255,255,255,0.6); backdrop-filter: blur(8px);">
      <button class="w-9 h-9 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors active:scale-95" @click="router.back()">
        <ArrowLeft :size="18" style="color: var(--color-text-secondary)" />
      </button>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold truncate" style="color: var(--color-text-primary)">引导式对话</p>
        <p class="text-xs" style="color: var(--color-text-tertiary)">
          {{ effectiveQuestionId !== 'demo' ? `题目 #${effectiveQuestionId.slice(-4)}` : '题目解析' }} · 第{{ messages.filter(m => m.role === 'assistant').length }}轮对话
        </p>
      </div>
      <span
        class="px-2 py-0.5 rounded-md text-xs font-medium"
        :style="{
          background: currentStage === 'COMPLETE' ? 'rgba(16,185,129,0.1)' : 'rgba(108,92,231,0.1)',
          color: currentStage === 'COMPLETE' ? '#10B981' : '#6C5CE7'
        }"
      >
        {{ currentStage === 'COMPLETE' ? '已完成' : currentStage }}
      </span>
    </div>

    <!-- Messages Area -->
    <div
      ref="messagesContainer"
      class="flex-1 overflow-y-auto p-4 space-y-4"
    >
      <!-- Error Alert -->
      <div v-if="error" class="rounded-xl p-4 bg-red-50/80 border border-red-100 text-sm text-red-600 mb-2">
        <p class="font-medium mb-1">出错了</p>
        <p class="text-xs">{{ error }}</p>
        <button class="mt-2 px-3 py-1 rounded-lg bg-red-100 text-red-600 text-xs font-medium hover:bg-red-200 transition-colors" @click="startGuidedChat(effectiveQuestionId)">
          重试
        </button>
      </div>

      <!-- Chat Bubbles -->
      <div v-for="msg in messages" :key="msg.id" :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']">

        <!-- AI Bubble -->
        <div v-if="msg.role === 'assistant'" class="max-w-[85%] md:max-w-[70%]">
          <div class="flex gap-2">
            <div class="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center flex-shrink-0 mt-0.5">
              <span class="text-white text-xs font-bold">AI</span>
            </div>
            <div>
              <div
                :class="[
                  'rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-line',
                  msg.stage === 'HINT'
                    ? '!bg-amber-50/80 border border-amber-100'
                    : 'bg-white/90 border border-gray-100/80 shadow-sm'
                ]"
                style="color: var(--color-text-primary)"
              >
                <template v-if="msg.stage === 'HINT'">
                  <div class="flex items-start gap-1.5 mb-1">
                    <Lightbulb :size="14" class="mt-0.5 flex-shrink-0 text-amber-500" />
                    <span class="text-xs font-medium text-amber-600">提示</span>
                  </div>
                </template>
                {{ msg.content }}
                <span v-if="msg.isStreaming" class="inline-block w-1.5 h-4 bg-purple-400 animate-pulse ml-0.5 align-text-bottom"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- User Bubble -->
        <div v-else class="max-w-[80%] md:max-w-[65%]">
          <div class="gradient-primary text-white rounded-2xl rounded-br-md px-4 py-3 text-sm leading-relaxed">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isLoading && !isStreaming" class="flex justify-start">
        <div class="flex gap-2">
          <div class="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center flex-shrink-0">
            <span class="text-white text-xs font-bold">AI</span>
          </div>
          <div class="bg-white/90 rounded-2xl px-5 py-3 border border-gray-100/80 shadow-sm flex gap-1.5 items-center">
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce"></span>
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="chat-input-area flex-shrink-0 border-t border-purple-50/80 p-3 lg:p-4">
      <!-- Toolbar -->
      <div v-if="!isComplete" class="flex items-center gap-2 mb-2.5 overflow-x-auto scrollbar-hide">
        <button
          class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-amber-50 transition-colors text-amber-600 whitespace-nowrap active:scale-95"
          @click="skipHint"
        >
          <SkipForward :size="13" />
          跳过提示
        </button>
        <button class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-blue-50 transition-colors text-blue-600 whitespace-nowrap active:scale-95">
          <Eye :size="13" />
          查看关键步骤
        </button>
        <button
          class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-red-50 transition-colors text-red-500 whitespace-nowrap active:scale-95"
          @click="endChat"
        >
          <Square :size="13" />
          结束对话
        </button>
      </div>

      <!-- Completed Banner -->
      <div v-else class="mb-2.5 px-4 py-2.5 rounded-xl bg-emerald-50/80 border border-emerald-100 text-center">
        <p class="text-sm font-medium text-emerald-700">对话已完成，继续加油！</p>
        <button class="mt-2 px-4 py-1.5 rounded-lg bg-emerald-100 text-emerald-600 text-xs font-medium hover:bg-emerald-200 transition-colors" @click="router.push('/')">
          返回首页
        </button>
      </div>

      <!-- Input Box -->
      <div class="flex items-end gap-2">
        <div class="flex-1 relative">
          <textarea
            v-model="inputText"
            :placeholder="isComplete ? '对话已结束' : '输入你的想法...'"
            :disabled="isComplete || isLoading || isStreaming"
            rows="1"
            class="w-full px-4 py-3 rounded-xl border border-gray-200/80 focus:border-purple-400 focus:ring-2 focus:ring-purple-100 outline-none resize-none text-sm transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            style="background: rgba(255,255,255,0.9); color: var(--color-text-primary)"
            @keydown="handleKeydown"
          ></textarea>
        </div>
        <button
          :disabled="!inputText.trim() || isLoading || isStreaming || isComplete"
          :class="[
            'w-11 h-11 rounded-xl flex items-center justify-center transition-all active:scale-95',
            (inputText.trim() && !isLoading && !isStreaming && !isComplete)
              ? 'gradient-primary shadow-md shadow-purple-200/50'
              : 'bg-gray-100 cursor-not-allowed'
          ]"
          @click="sendMessage_action"
        >
          <Send v-if="inputText.trim() && !isLoading && !isComplete" :size="18" class="text-white" />
          <span v-else class="text-gray-400 text-sm">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-input-area {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
}

@media (max-width: 1023px) {
  .guided-chat-view {
    height: calc(100vh - 64px - 72px);
  }
  .chat-input-area {
    padding-bottom: max(12px, env(safe-area-inset-bottom));
  }
}

@media (min-width: 1024px) {
  .guided-chat-view {
    height: calc(100vh - 64px);
  }
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
