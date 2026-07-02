<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Lightbulb, SkipForward, Eye, Square, Send, BookmarkPlus } from 'lucide-vue-next'
import { useChat } from '@/composables/useChat'
import { useMistakeBookStore } from '@/stores/mistakeBook'

const route = useRoute()
const router = useRouter()
const mistakeStore = useMistakeBookStore()

const toastMsg = ref('')

const props = defineProps<{ questionId?: string }>()

const {
  messages,
  currentStage,
  isLoading,
  isStreaming,
  isComplete,
  error,
  startGuidedChat,
  sendUserMessage,
  scrollToBottom,
} = useChat()

const messagesContainer = ref<HTMLElement | null>(null)
const inputText = ref('')

const effectiveQuestionId = computed(() =>
  (route.query.questionId as string) || props.questionId || 'demo'
)

const assistantRounds = computed(() =>
  messages.value.filter(m => m.role === 'assistant').length
)

const stageLabel = computed(() =>
  currentStage.value === 'COMPLETE' ? '已完成' : currentStage.value
)

onMounted(async () => {
  await startGuidedChat(effectiveQuestionId.value)
  scrollToBottom(messagesContainer.value)
})

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

async function sendMessageAction() {
  if (!inputText.value.trim() || isLoading.value || isStreaming.value) return

  const text = inputText.value.trim()
  inputText.value = ''
  await sendUserMessage(text)
  scrollToBottom(messagesContainer.value)
}

function skipHint() {
  inputText.value = '跳过提示，请继续'
  sendMessageAction()
}

function endChat() {
  router.push('/')
}

function addToMistakeBook(aiContent: string, prevUserContent?: string) {
  const subject = (route.query.subject as string) || '数据结构'
  const content = prevUserContent || aiContent.slice(0, 100)
  mistakeStore.addMistake({
    questionContent: content,
    subject,
    knowledgeTags: [],
    errorReason: 'AI 提示后仍回答错误',
  })
  toastMsg.value = '已加入错题本'
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessageAction()
  }
}
</script>

<template>
  <div class="guided-chat-view">
    <header class="chat-header">
      <button class="icon-btn" aria-label="返回" @click="router.back()">
        <ArrowLeft :size="18" />
      </button>
      <div class="chat-title-block">
        <p class="chat-title">引导式对话</p>
        <p class="chat-subtitle">
          {{ effectiveQuestionId !== 'demo' ? `题目 #${effectiveQuestionId.slice(-4)}` : '题目解析' }}
          · 第 {{ assistantRounds }} 轮对话
        </p>
      </div>
      <span class="stage-badge" :class="{ complete: currentStage === 'COMPLETE' }">
        {{ stageLabel }}
      </span>
    </header>

    <transition name="toast-fade">
      <div v-if="toastMsg" class="toast-bar">{{ toastMsg }}</div>
    </transition>

    <main ref="messagesContainer" class="messages-area">
      <section v-if="error" class="error-alert">
        <p class="error-title">出错了</p>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="startGuidedChat(effectiveQuestionId)">重试</button>
      </section>

      <article
        v-for="(msg, idx) in messages"
        :key="msg.id"
        class="message-row"
        :class="msg.role === 'user' ? 'message-row--user' : 'message-row--assistant'"
      >
        <template v-if="msg.role === 'assistant'">
          <div class="ai-avatar">AI</div>
          <div class="message-stack">
            <div class="message-bubble ai-bubble" :class="{ hint: msg.stage === 'HINT' }">
              <div v-if="msg.stage === 'HINT'" class="hint-label">
                <Lightbulb :size="14" />
                <span>提示</span>
              </div>
              <p>{{ msg.content }}</p>
              <span v-if="msg.isStreaming" class="stream-caret"></span>
            </div>
            <button
              v-if="!msg.isStreaming && msg.stage && ['HINT', 'PROBE'].includes(msg.stage)"
              class="mistake-add-btn"
              @click="addToMistakeBook(msg.content, idx > 0 ? messages[idx - 1]?.content : '')"
            >
              <BookmarkPlus :size="13" />
              加入错题本
            </button>
          </div>
        </template>

        <div v-else class="message-bubble user-bubble">
          <p>{{ msg.content }}</p>
        </div>
      </article>

      <div v-if="isLoading && !isStreaming" class="message-row message-row--assistant">
        <div class="ai-avatar">AI</div>
        <div class="typing-bubble">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </main>

    <footer class="chat-input-area">
      <div v-if="!isComplete" class="quick-actions">
        <button class="quick-btn quick-btn--amber" @click="skipHint">
          <SkipForward :size="14" />
          跳过提示
        </button>
        <button class="quick-btn quick-btn--blue" type="button">
          <Eye :size="14" />
          查看关键步骤
        </button>
        <button class="quick-btn quick-btn--red" @click="endChat">
          <Square :size="14" />
          结束对话
        </button>
      </div>

      <div v-else class="complete-banner">
        <p>对话已完成，继续加油！</p>
        <button @click="router.push('/')">返回首页</button>
      </div>

      <div class="input-row">
        <textarea
          v-model="inputText"
          :placeholder="isComplete ? '对话已结束' : '输入你的想法...'"
          :disabled="isComplete || isLoading || isStreaming"
          rows="1"
          class="chat-textarea"
          @keydown="handleKeydown"
        ></textarea>
        <button
          class="send-btn"
          :disabled="!inputText.trim() || isLoading || isStreaming || isComplete"
          aria-label="发送"
          @click="sendMessageAction"
        >
          <Send v-if="inputText.trim() && !isLoading && !isComplete" :size="18" />
          <span v-else>→</span>
        </button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.guided-chat-view {
  height: min(720px, calc(100vh - 11rem));
  min-height: 560px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(75, 85, 99, 0.1);
  border-radius: 24px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(248, 250, 252, 0.9)),
    radial-gradient(circle at 14% 0%, rgba(13, 148, 136, 0.08), transparent 32%);
  box-shadow: 0 20px 45px -36px rgba(15, 23, 42, 0.44);
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  flex-shrink: 0;
  padding: 0.9rem 1rem;
  border-bottom: 1px solid rgba(75, 85, 99, 0.08);
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(12px);
}

.icon-btn {
  width: 2.25rem;
  height: 2.25rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 0;
  border-radius: 12px;
  color: var(--color-text-secondary);
  background: transparent;
  cursor: pointer;
}

.icon-btn:hover {
  color: #0d9488;
  background: rgba(13, 148, 136, 0.08);
}

.chat-title-block {
  min-width: 0;
  flex: 1;
}

.chat-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--color-text-primary);
}

.chat-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.78rem;
  color: var(--color-text-tertiary);
}

.stage-badge {
  flex-shrink: 0;
  padding: 0.32rem 0.58rem;
  border-radius: 10px;
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
  font-size: 0.75rem;
  font-weight: 800;
}

.stage-badge.complete {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.15rem;
}

.error-alert {
  margin-bottom: 1rem;
  padding: 1rem;
  border: 1px solid rgba(239, 68, 68, 0.18);
  border-radius: 16px;
  color: #dc2626;
  background: rgba(254, 242, 242, 0.86);
}

.error-alert p {
  margin: 0;
  font-size: 0.85rem;
}

.error-title {
  margin-bottom: 0.25rem !important;
  font-weight: 800;
}

.retry-btn {
  margin-top: 0.6rem;
  padding: 0.4rem 0.75rem;
  border: 0;
  border-radius: 10px;
  color: #dc2626;
  background: rgba(239, 68, 68, 0.1);
  font-weight: 700;
  cursor: pointer;
}

.message-row {
  display: flex;
  gap: 0.65rem;
  margin-bottom: 1rem;
}

.message-row--user {
  justify-content: flex-end;
}

.message-row--assistant {
  justify-content: flex-start;
}

.ai-avatar {
  width: 2rem;
  height: 2rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  margin-top: 0.15rem;
  border-radius: 11px;
  color: #fff;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  font-size: 0.75rem;
  font-weight: 900;
}

.message-stack {
  max-width: min(760px, 78%);
}

.message-bubble {
  border-radius: 18px;
  padding: 0.85rem 1rem;
  font-size: 0.92rem;
  line-height: 1.72;
}

.message-bubble p {
  margin: 0;
  white-space: pre-wrap;
}

.ai-bubble {
  color: var(--color-text-primary);
  border: 1px solid rgba(75, 85, 99, 0.09);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 24px -22px rgba(15, 23, 42, 0.42);
}

.ai-bubble.hint {
  border-color: rgba(245, 158, 11, 0.18);
  background: rgba(255, 251, 235, 0.88);
}

.user-bubble {
  max-width: min(680px, 72%);
  color: #fff;
  border-bottom-right-radius: 6px;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  box-shadow: 0 12px 24px -18px rgba(13, 148, 136, 0.9);
}

.hint-label {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-bottom: 0.3rem;
  color: #d97706;
  font-size: 0.78rem;
  font-weight: 800;
}

.stream-caret {
  display: inline-block;
  width: 0.36rem;
  height: 1rem;
  margin-left: 0.18rem;
  vertical-align: text-bottom;
  background: #0d9488;
  animation: caretPulse 0.8s infinite;
}

.mistake-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.28rem;
  margin-top: 0.45rem;
  padding: 0.35rem 0.55rem;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #d97706;
  background: rgba(245, 158, 11, 0.07);
  font-size: 0.75rem;
  font-weight: 800;
  cursor: pointer;
}

.mistake-add-btn:hover {
  border-color: rgba(245, 158, 11, 0.18);
  background: rgba(245, 158, 11, 0.12);
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.85rem 1rem;
  border: 1px solid rgba(75, 85, 99, 0.09);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
}

.typing-bubble span {
  width: 0.45rem;
  height: 0.45rem;
  border-radius: 50%;
  background: #5eead4;
  animation: bounce 0.9s infinite;
}

.typing-bubble span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-bubble span:nth-child(3) {
  animation-delay: 0.3s;
}

.chat-input-area {
  flex-shrink: 0;
  padding: 0.9rem 1rem 1rem;
  border-top: 1px solid rgba(75, 85, 99, 0.08);
  background: rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(16px) saturate(180%);
}

.quick-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.65rem;
  overflow-x: auto;
}

.quick-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.32rem;
  flex-shrink: 0;
  padding: 0.46rem 0.75rem;
  border: 0;
  border-radius: 11px;
  font-size: 0.78rem;
  font-weight: 800;
  cursor: pointer;
}

.quick-btn--amber {
  color: #d97706;
  background: rgba(245, 158, 11, 0.1);
}

.quick-btn--blue {
  color: #2563eb;
  background: rgba(37, 99, 235, 0.09);
}

.quick-btn--red {
  color: #dc2626;
  background: rgba(239, 68, 68, 0.09);
}

.complete-banner {
  margin-bottom: 0.65rem;
  padding: 0.8rem 1rem;
  border: 1px solid rgba(16, 185, 129, 0.16);
  border-radius: 16px;
  text-align: center;
  background: rgba(236, 253, 245, 0.86);
}

.complete-banner p {
  margin: 0 0 0.5rem;
  color: #047857;
  font-size: 0.9rem;
  font-weight: 800;
}

.complete-banner button {
  padding: 0.42rem 0.9rem;
  border: 0;
  border-radius: 10px;
  color: #047857;
  background: rgba(16, 185, 129, 0.12);
  font-weight: 800;
  cursor: pointer;
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 0.65rem;
}

.chat-textarea {
  width: 100%;
  min-height: 2.75rem;
  max-height: 8rem;
  padding: 0.78rem 0.95rem;
  border: 1px solid rgba(75, 85, 99, 0.14);
  border-radius: 14px;
  outline: none;
  resize: vertical;
  color: var(--color-text-primary);
  background: rgba(255, 255, 255, 0.92);
  font: inherit;
  font-size: 0.92rem;
  line-height: 1.45;
}

.chat-textarea:focus {
  border-color: rgba(13, 148, 136, 0.48);
  box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.1);
}

.chat-textarea:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.send-btn {
  width: 2.75rem;
  height: 2.75rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  border: 0;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  box-shadow: 0 12px 24px -18px rgba(13, 148, 136, 0.9);
  cursor: pointer;
}

.send-btn:disabled {
  color: #94a3b8;
  background: #f1f5f9;
  box-shadow: none;
  cursor: not-allowed;
}

.toast-bar {
  position: fixed;
  top: 5rem;
  left: 50%;
  z-index: var(--z-50);
  transform: translateX(-50%);
  padding: 0.55rem 1.2rem;
  border-radius: 999px;
  color: white;
  background: #0d9488;
  font-size: 0.85rem;
  font-weight: 800;
  box-shadow: 0 12px 24px -16px rgba(13, 148, 136, 0.9);
  pointer-events: none;
}

.toast-fade-enter-active {
  animation: toastIn 0.3s ease;
}

.toast-fade-leave-active {
  animation: toastOut 0.3s ease;
}

@keyframes caretPulse {
  50% {
    opacity: 0.35;
  }
}

@keyframes bounce {
  50% {
    transform: translateY(-3px);
  }
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
  to {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
}

@media (max-width: 767px) {
  .guided-chat-view {
    height: calc(100vh - 12.5rem);
    min-height: 520px;
    border-radius: 18px;
  }

  .messages-area {
    padding: 0.9rem;
  }

  .message-stack,
  .user-bubble {
    max-width: 86%;
  }

  .chat-input-area {
    padding-bottom: max(0.9rem, env(safe-area-inset-bottom));
  }
}
</style>
