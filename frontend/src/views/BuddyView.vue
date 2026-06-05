<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { Sparkles, Send, Users, MessageCircle, Swords, GraduationCap, Heart, Brain, ArrowLeft, Loader2 } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import Avatar from '@/components/ui/Avatar.vue'
import { startSession, sendMessage, endSession } from '@/api/studyBuddy'
import type { BuddyRole, BuddyMode, BuddyMessage } from '@/api/studyBuddy'

type StageType = 'select' | 'chat'
const stage = ref<StageType>('select')
const isLoading = ref(false)
const errorMsg = ref('')

interface RoleDef {
  key: BuddyRole; name: string; icon: any; desc: string; color: string; gradient: string
}
const roles: RoleDef[] = [
  { key: 'scholar', name: '学霸', icon: GraduationCap, desc: '知识渊博，喜欢出题考你', color: '#7c3aed', gradient: 'linear-gradient(135deg, #7c3aed, #a78bfa)' },
  { key: 'hardworking', name: '努力型', icon: Heart, desc: '勤奋踏实，互相鼓励陪伴', color: '#f59e0b', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { key: 'discussion', name: '讨论型', icon: Brain, desc: '喜欢辩论，激发深度思考', color: '#059669', gradient: 'linear-gradient(135deg, #059669, #34d399)' },
]

interface ModeDef {
  key: BuddyMode; name: string; icon: any; desc: string
}
const modes: ModeDef[] = [
  { key: 'debate', name: '辩论', icon: Swords, desc: 'AI提出对立观点，你来反驳' },
  { key: 'collaborate', name: '协作', icon: Users, desc: '共同解决问题，互相启发' },
  { key: 'quiz', name: '测验', icon: MessageCircle, desc: 'AI出题，你来回答' },
]

const selectedRole = ref<BuddyRole>('scholar')
const selectedMode = ref<BuddyMode>('collaborate')
const topicInput = ref('')

const sessionId = ref('')
const messages = ref<BuddyMessage[]>([])
const currentInput = ref('')
const chatContainer = ref<HTMLElement>()
const summary = ref('')

const currentRoleDef = computed(() => roles.find(r => r.key === selectedRole.value))

async function handleStart() {
  errorMsg.value = ''
  isLoading.value = true
  try {
    const session = await startSession(selectedRole.value, selectedMode.value, topicInput.value || undefined)
    sessionId.value = session.session_id
    messages.value = [{ role: 'buddy', content: session.greeting }]
    stage.value = 'chat'
    await nextTick()
    scrollToBottom()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '启动会话失败'
  } finally {
    isLoading.value = false
  }
}

async function handleSend() {
  const text = currentInput.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  currentInput.value = ''
  await nextTick()
  scrollToBottom()

  isLoading.value = true
  try {
    const res = await sendMessage(sessionId.value, text)
    messages.value.push(res)
    await nextTick()
    scrollToBottom()
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '发送失败'
  } finally {
    isLoading.value = false
  }
}

async function handleEnd() {
  isLoading.value = true
  try {
    const res = await endSession(sessionId.value)
    summary.value = res.summary
  } catch { /* ignore */ }
  isLoading.value = false
}

function scrollToBottom() {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function reset() {
  stage.value = 'select'
  messages.value = []
  sessionId.value = ''
  summary.value = ''
}
</script>

<template>
  <div class="buddy-page">
    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>

    <!-- Stage: Select -->
    <div v-if="stage === 'select'" class="select-stage">
      <!-- Warm intro -->
      <div class="buddy-intro">
        <p class="buddy-intro__overline font-serif">选择你的 AI 学习伙伴</p>
        <h1 class="buddy-intro__title">今天，谁陪你一起学习？</h1>
        <p class="buddy-intro__desc">不同的研友有不同的性格和教学风格，选一个最适合你的</p>
      </div>

      <!-- Roles -->
      <div class="role-grid">
        <button
          v-for="role in roles" :key="role.key"
          :class="['role-card', { active: selectedRole === role.key }]"
          :style="{ '--role-color': role.color, '--role-gradient': role.gradient }"
          @click="selectedRole = role.key"
        >
          <div class="role-card__glow" aria-hidden="true"></div>
          <div class="role-card__avatar" :style="{ background: role.gradient }">
            <component :is="role.icon" :size="28" class="text-white" />
          </div>
          <div class="role-card__info">
            <span class="role-card__name">{{ role.name }}</span>
            <span class="role-card__desc">{{ role.desc }}</span>
          </div>
          <div v-if="selectedRole === role.key" class="role-card__check" :style="{ background: role.gradient }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="role-card__check-icon"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
        </button>
      </div>

      <!-- Modes -->
      <div class="mode-section">
        <p class="mode-label">互动模式</p>
        <div class="mode-grid">
          <button
            v-for="mode in modes" :key="mode.key"
            :class="['mode-btn', { active: selectedMode === mode.key }]"
            @click="selectedMode = mode.key"
          >
            <component :is="mode.icon" :size="20" class="mode-btn__icon" />
            <span class="mode-btn__name">{{ mode.name }}</span>
            <span class="mode-btn__desc">{{ mode.desc }}</span>
          </button>
        </div>
      </div>

      <!-- Topic -->
      <div class="topic-section">
        <label class="topic-label">讨论主题 <span class="topic-label__hint">选填</span></label>
        <input
          v-model="topicInput"
          class="topic-input"
          placeholder="例如：二叉树遍历、虚拟内存、TCP拥塞控制..."
          @keyup.enter="handleStart"
        />
      </div>

      <Button
        variant="primary" size="lg" class="start-btn"
        :loading="isLoading" block
        @click="handleStart"
      >
        <Sparkles :size="18" />
        开始对话
      </Button>
    </div>

    <!-- Stage: Chat -->
    <div v-if="stage === 'chat'" class="chat-stage">
      <!-- Top bar -->
      <div class="chat-topbar" v-if="currentRoleDef">
        <button class="chat-back" @click="reset">
          <ArrowLeft :size="18" />
        </button>
        <div class="chat-topbar__role" :style="{ background: currentRoleDef.gradient }">
          <component :is="currentRoleDef.icon" :size="15" class="text-white" />
          <span>{{ currentRoleDef.name }} · {{ modes.find(m => m.key === selectedMode)?.name }}模式</span>
        </div>
      </div>

      <!-- Messages -->
      <div ref="chatContainer" class="chat-messages">
        <div v-for="(msg, i) in messages" :key="i" :class="['chat-bubble', msg.role]">
          <Avatar
            v-if="msg.role === 'buddy'"
            size="sm"
            :name="currentRoleDef?.name || 'AI'"
            class="bubble-avatar"
          />
          <div class="bubble-content" :class="msg.role" :style="msg.role === 'buddy' ? { borderLeftColor: currentRoleDef?.color + '40' } : {}">
            <p>{{ msg.content }}</p>
          </div>
        </div>
        <div v-if="isLoading" class="chat-bubble buddy">
          <div class="bubble-content buddy typing">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- Summary -->
      <div v-if="summary" class="summary-card surface-glow">
        <p class="summary-card__label font-serif">讨论摘要</p>
        <p class="summary-card__text">{{ summary }}</p>
      </div>

      <!-- Input -->
      <div class="chat-input-row">
        <input
          v-model="currentInput"
          class="chat-input"
          placeholder="输入消息..."
          :disabled="isLoading"
          @keyup.enter="handleSend"
        />
        <button class="send-btn" :disabled="!currentInput.trim() || isLoading" @click="handleSend" aria-label="发送消息">
          <Send :size="18" />
        </button>
      </div>

      <div class="end-row">
        <Button variant="outline" size="sm" @click="handleEnd" :disabled="isLoading">
          结束会话 · 查看摘要
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.buddy-page { max-width: 720px; margin: 0 auto; padding: 1.5rem; }

.error-toast {
  background: var(--color-bg-danger-soft);
  color: var(--color-danger-600);
  padding: 0.7rem 1rem;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
  font-size: 0.85rem;
  border: 1px solid var(--color-danger-200);
}

/* ============================
   INTRO — Warm & personal
   ============================ */
.buddy-intro {
  text-align: center;
  margin-bottom: 2rem;
}
.buddy-intro__overline {
  font-size: 0.9rem;
  color: var(--color-amber-600);
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}
.buddy-intro__title {
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.4rem;
}
.buddy-intro__desc {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

/* ============================
   ROLE CARDS — Character-driven
   ============================ */
.role-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.role-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
  padding: 1.5rem 1rem;
  border-radius: var(--radius-xl);
  border: 2px solid var(--color-border-light);
  background: var(--surface-paper-bg);
  cursor: pointer;
  transition: all var(--transition-bounce);
  overflow: hidden;
  text-align: center;
}
.role-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-border);
}

.role-card.active {
  border-color: var(--role-color);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--role-color) 12%, transparent),
              0 8px 30px color-mix(in srgb, var(--role-color) 15%, transparent);
  background: linear-gradient(180deg,
    color-mix(in srgb, var(--role-color) 4%, transparent) 0%,
    var(--surface-paper-bg) 50%);
}

.role-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 0%, var(--role-gradient), transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}
.role-card.active .role-card__glow {
  opacity: 0.08;
}

.role-card__avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px color-mix(in srgb, var(--role-color) 35%, transparent);
  position: relative;
  z-index: 1;
  transition: transform var(--transition-normal);
}
.role-card:hover .role-card__avatar {
  transform: scale(1.05);
}

.role-card__info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  position: relative;
  z-index: 1;
}
.role-card__name {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-text-primary);
}
.role-card__desc {
  font-size: 0.78rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.role-card__check {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.role-card__check-icon {
  width: 14px;
  height: 14px;
}

/* ============================
   MODE SELECTOR
   ============================ */
.mode-section {
  margin-bottom: 1.5rem;
}
.mode-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.6rem;
  display: block;
}

.mode-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.mode-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.9rem 0.5rem;
  border-radius: var(--radius-lg);
  border: 1.5px solid var(--color-border-light);
  background: var(--color-bg-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-secondary);
}
.mode-btn:hover {
  border-color: var(--color-border);
  background: var(--color-bg-secondary);
}
.mode-btn.active {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  color: var(--color-primary-600);
}
.mode-btn__icon {
  transition: transform var(--transition-fast);
}
.mode-btn.active .mode-btn__icon {
  color: var(--color-primary-500);
}
.mode-btn__name {
  font-weight: 600;
  font-size: 0.88rem;
}
.mode-btn__desc {
  font-size: 0.7rem;
  opacity: 0.6;
  line-height: 1.3;
}

/* ============================
   TOPIC INPUT
   ============================ */
.topic-section {
  margin-bottom: 1.5rem;
}
.topic-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 0.4rem;
  display: block;
}
.topic-label__hint {
  font-weight: 400;
  color: var(--color-text-muted);
  font-size: 0.78rem;
}
.topic-input {
  width: 100%;
  padding: 0.7rem 0.9rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  outline: none;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  box-sizing: border-box;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  font-family: inherit;
}
.topic-input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-border-focus);
}

.start-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* ============================
   CHAT STAGE
   ============================ */
.chat-stage {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.chat-topbar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0;
  margin-bottom: 0.8rem;
  border-bottom: 1px solid var(--color-border-light);
}
.chat-back {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  border: none;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}
.chat-back:hover {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}
.chat-topbar__role {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.9rem;
  border-radius: 999px;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.chat-bubble {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}
.chat-bubble.user {
  flex-direction: row-reverse;
}

.bubble-content {
  max-width: 72%;
  padding: 0.75rem 1.1rem;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.6;
}
.bubble-content.buddy {
  background: var(--surface-paper-bg);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  border-bottom-left-radius: 6px;
  border-left: 3px solid var(--color-primary-300);
}
.bubble-content.user {
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  color: white;
  border-bottom-right-radius: 6px;
}

.typing {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 1rem 1.5rem;
}
.dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: dotBounce 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Summary */
.summary-card {
  margin: 0.8rem 0;
  padding: 1rem 1.2rem;
}
.summary-card__label {
  font-size: 0.8rem;
  color: var(--color-amber-600);
  margin-bottom: 0.3rem;
  letter-spacing: 0.03em;
}
.summary-card__text {
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  line-height: 1.65;
}

/* Input */
.chat-input-row {
  display: flex;
  gap: 0.5rem;
  padding: 0.8rem 0;
  border-top: 1px solid var(--color-border-light);
}
.chat-input {
  flex: 1;
  padding: 0.7rem 1rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-lg);
  font-size: 0.9rem;
  outline: none;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color var(--transition-fast);
}
.chat-input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-border-focus);
}
.send-btn {
  width: 44px; height: 44px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--color-primary-500), var(--color-primary-700));
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.25);
}
.send-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
  box-shadow: none;
}
.send-btn:not(:disabled):hover {
  transform: scale(1.06);
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
}
.send-btn:not(:disabled):active {
  transform: scale(0.95);
}

.end-row {
  text-align: center;
  margin-top: 0.5rem;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 640px) {
  .buddy-page { padding: 1rem; }
  .role-grid, .mode-grid { grid-template-columns: 1fr; }
  .bubble-content { max-width: 85%; }
  .buddy-intro__title { font-size: 1.3rem; }
}
</style>
