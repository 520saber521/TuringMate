<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Lightbulb, SkipForward, Eye, Square } from 'lucide-vue-next'
import type { ChatMessage, TutorStage } from '@/types/chat'

const props = defineProps<{ questionId?: string }>()
const router = useRouter()

const messages = ref<ChatMessage[]>([
  {
    id: '1',
    role: 'assistant',
    content: '同学你好！看到这道题，你觉得它考查的核心知识点是什么呢？\n\n💡 提示：可以想想单链表的遍历和删除操作有什么需要注意的地方~',
    timestamp: new Date().toISOString(),
    stage: 'QUESTION',
  },
])
const inputText = ref('')
const currentStage = ref<TutorStage>('HINT')
const isLoading = ref(false)

async function sendMessage() {
  if (!inputText.value.trim() || isLoading.value) return

  const userMsg: ChatMessage = {
    id: `msg_${Date.now()}`,
    role: 'user',
    content: inputText.value.trim(),
    timestamp: new Date().toISOString(),
  }
  messages.value.push(userMsg)
  const text = inputText.value
  inputText.value = ''
  isLoading.value = true

  await nextTick()
  scrollToBottom()

  // Mock AI response
  setTimeout(() => {
    const responses: Record<TutorStage, string> = {
      HINT: '很好的思考方向！那我们进一步想一下：在遍历链表时，如果要删除当前结点，我们需要知道什么信息？\n\n💡 提示：想一想删除操作需要的前驱结点...',
      PROBE: '对！那你能不能用自己的话说说为什么需要这样处理？\n\n✨ 这能帮我确认你是否真正理解了原理~',
      AFFIRM: '非常棒！你的理解完全正确！🎉\n\n现在我们已经掌握了核心思路，想不想看看这个知识点还能怎么拓展应用？',
      EXTEND: '拓展思考：如果把「单链表」换成「双向链表」，解题思路会有什么变化？',
      COMPLETE: '今天的引导讲解就到这里！总结要点：\n1. 链表遍历时维护前驱指针\n2. 注意边界情况\n继续保持这样的思考方式！💪',
      QUESTION: '同学你好！看到这道题，你觉得它考查的核心知识点是什么呢？',
    }

    const stages: TutorStage[] = ['HINT', 'PROBE', 'AFFIRM', 'EXTEND', 'COMPLETE']
    const nextStageIdx = Math.min(stages.indexOf(currentStage.value) + 1, stages.length - 1)
    currentStage.value = stages[nextStageIdx]

    const aiMsg: ChatMessage = {
      id: `msg_${Date.now()}_ai`,
      role: 'assistant',
      content: responses[currentStage.value],
      timestamp: new Date().toISOString(),
      stage: currentStage.value,
    }
    messages.value.push(aiMsg)
    isLoading.value = false
    scrollToBottom()
  }, 1200)
}

function scrollToBottom() {
  // TODO: scroll chat container to bottom
}

function skipHint() {
  inputText.value = '跳过提示，请继续'
  sendMessage()
}
</script>

<template>
  <div class="guided-chat-view h-[calc(100vh-4rem)] flex flex-col animate-fade-in-up">
    <!-- Header -->
    <div class="flex items-center gap-3 px-4 py-3 border-b border-gray-100 flex-shrink-0">
      <button class="w-9 h-9 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors" @click="router.back()">
        <ArrowLeft :size="18" style="color: var(--color-text-secondary)" />
      </button>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold truncate" style="color: var(--color-text-primary)">引导式对话</p>
        <p class="text-xs" style="color: var(--color-text-tertiary)">
          {{ questionId || '题目解析中' }} · 第{{ messages.filter(m => m.role === 'assistant').length }}轮对话
        </p>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- Question Context Card -->
      <div class="glass-card !rounded-xl p-4 max-w-md">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-lg bg-purple-50 flex items-center justify-center flex-shrink-0">
            <span class="text-sm font-bold" style="color: var(--color-primary)">DS</span>
          </div>
          <div>
            <p class="text-xs font-medium mb-1" style="color: var(--color-primary)">数据结构 · 单链表</p>
            <p class="text-sm leading-relaxed" style="color: var(--color-text-secondary)">
              设单链表的表头指针为 L，设计算法删除链表中所有值等于 x 的结点。
            </p>
          </div>
        </div>
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
                    ? '!bg-amber-50 border border-amber-100'
                    : 'bg-white border border-gray-100 shadow-sm'
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
              </div>
            </div>
          </div>
        </div>

        <!-- User Bubble -->
        <div v-else class="max-w-[80%] md:max-w-[65%]">
          <div class="gradient-primary text-white rounded-2xl px-4 py-3 text-sm leading-relaxed">
            {{ msg.content }}
          </div>
        </div>
      </div>

      <!-- Typing Indicator -->
      <div v-if="isLoading" class="flex justify-start">
        <div class="flex gap-2">
          <div class="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center flex-shrink-0">
            <span class="text-white text-xs font-bold">AI</span>
          </div>
          <div class="bg-white rounded-2xl px-5 py-3 border border-gray-100 shadow-sm flex gap-1.5">
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce"></span>
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 rounded-full bg-purple-300 animate-bounce" style="animation-delay: 300ms"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="flex-shrink-0 border-t border-gray-100 bg-white/80 backdrop-blur-xl p-4">
      <!-- Toolbar -->
      <div class="flex items-center gap-2 mb-3 overflow-x-auto">
        <button
          v-if="currentStage !== 'COMPLETE'"
          class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-amber-50 transition-colors text-amber-600 whitespace-nowrap"
          @click="skipHint"
        >
          <SkipForward :size="13" />
          跳过提示
        </button>
        <button class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-blue-50 transition-colors text-blue-600 whitespace-nowrap">
          <Eye :size="13" />
          查看关键步骤
        </button>
        <button
          v-if="currentStage !== 'COMPLETE'"
          class="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-red-50 transition-colors text-red-500 whitespace-nowrap"
        >
          <Square :size="13" />
          结束对话
        </button>
      </div>

      <!-- Input Box -->
      <div class="flex items-end gap-2">
        <div class="flex-1 relative">
          <textarea
            v-model="inputText"
            placeholder="输入你的想法..."
            rows="1"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-purple-400 focus:ring-2 focus:ring-purple-100 outline-none resize-none text-sm transition-all"
            style="background: var(--color-bg-white); color: var(--color-text-primary)"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
        </div>
        <button
          :disabled="!inputText.trim() || isLoading"
          :class="[
            'w-11 h-11 rounded-xl flex items-center justify-center transition-all',
            (inputText.trim() && !isLoading) ? 'gradient-primary shadow-md shadow-purple-200 active:scale-95' : 'bg-gray-100 cursor-not-allowed'
          ]"
          @click="sendMessage"
        >
          <span class="text-white text-sm">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-6px); }
}
.animate-bounce {
  animation: bounce 1.4s ease-in-out infinite;
}
</style>
