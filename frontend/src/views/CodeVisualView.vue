<script setup lang="ts">
/**
 * CodeVisualView - 代码可视化页面
 * 代码输入 → 后端沙箱执行 → 步骤播放器展示运行过程
 * 接入后端 /visualize/execute API
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Play, Pause, SkipForward, SkipBack, Code2, RotateCcw } from 'lucide-vue-next'
import { executeAndVisualize, type VisualStep, type VisualizeResult } from '@/api/visualization'

const router = useRouter()

const sampleCode = `def delete_x(L, x):
    """删除链表中所有值为 x 的结点"""
    pre = L          # 前驱指针
    cur = L.next     # 当前结点
    while cur:
        if cur.data == x:
            pre.next = cur.next
        else:
            pre = cur
        cur = cur.next`

const code = ref(sampleCode)
const language = ref('python')
const isExecuting = ref(false)
const error = ref<string | null>(null)
const result = ref<VisualizeResult | null>(null)

const currentStep = ref(0)
const isPlaying = ref(false)
let playTimer: ReturnType<typeof setInterval> | null = null

const totalSteps = computed(() => result.value?.total_steps || 0)
const currentStepData = computed(() => result.value?.steps[currentStep.value] || null)

async function executeCode() {
  if (!code.value.trim() || isExecuting.value) return

  isExecuting.value = true
  error.value = null
  result.value = null
  currentStep.value = 0

  try {
    const res = await executeAndVisualize(code.value, language.value)
    result.value = res
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || '执行失败'
  } finally {
    isExecuting.value = false
  }
}

function togglePlay() {
  if (isPlaying.value) {
    pausePlay()
  } else {
    startPlay()
  }
}

function startPlay() {
  if (!result.value || currentStep.value >= totalSteps.value - 1) {
    currentStep.value = 0
  }
  isPlaying.value = true
  playTimer = setInterval(() => {
    if (currentStep.value < totalSteps.value - 1) {
      currentStep.value++
    } else {
      pausePlay()
    }
  }, 1500)
}

function pausePlay() {
  isPlaying.value = false
  if (playTimer) {
    clearInterval(playTimer)
    playTimer = null
  }
}

function stepForward() {
  pausePlay()
  if (currentStep.value < totalSteps.value - 1) {
    currentStep.value++
  }
}

function stepBack() {
  pausePlay()
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

function resetExecution() {
  pausePlay()
  currentStep.value = 0
}

// 代码行高亮
const codeLines = computed(() => code.value.split('\n'))
const highlightedLine = computed(() => currentStepData.value?.line || 0)
</script>

<template>
  <div class="code-visual-view animate-fade-in-up pb-20 lg:pb-0">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors" @click="router.back()">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">代码可视化</h2>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Code Panel -->
      <div class="glass-card !rounded-2xl p-4 overflow-hidden">
        <div class="flex items-center justify-between mb-3 px-1">
          <p class="text-xs font-medium" style="color: var(--color-text-secondary)">代码</p>
          <button
            :disabled="isExecuting"
            :class="[
              'px-4 py-1.5 rounded-lg text-xs font-medium flex items-center gap-1.5 transition-all',
              isExecuting ? 'bg-purple-100 text-purple-400 cursor-not-allowed' : 'gradient-primary text-white shadow-sm active:scale-95'
            ]"
            @click="executeCode"
          >
            <Play :size="12" />
            {{ isExecuting ? '执行中...' : '运行' }}
          </button>
        </div>
        <div class="code-editor rounded-xl overflow-hidden">
          <div
            v-for="(line, idx) in codeLines"
            :key="idx"
            :class="[
              'px-4 py-0.5 text-sm font-mono leading-relaxed transition-colors',
              result && highlightedLine === idx + 1
                ? 'bg-purple-500/20 text-white'
                : 'text-purple-300'
            ]"
          >
            <span class="inline-block w-8 text-right mr-4 text-purple-500/50 text-xs select-none">{{ idx + 1 }}</span>
            {{ line }}
          </div>
        </div>
      </div>

      <!-- Visual Panel -->
      <div class="glass-card !rounded-2xl p-4 min-h-[280px]">
        <p class="text-xs font-medium mb-3 px-1" style="color: var(--color-text-secondary)">执行过程</p>

        <!-- Error -->
        <div v-if="error" class="rounded-xl p-4 bg-red-900/20 border border-red-800/30 text-sm text-red-400">
          <p class="font-medium mb-1">执行失败</p>
          <p class="text-xs">{{ error }}</p>
        </div>

        <!-- No Result -->
        <div v-else-if="!result" class="flex flex-col items-center justify-center py-8">
          <Code2 :size="40" class="text-purple-300/40 mb-3" />
          <p class="text-sm" style="color: var(--color-text-tertiary)">点击「运行」查看代码执行过程</p>
        </div>

        <!-- Steps Display -->
        <div v-else class="space-y-3">
          <!-- Step Description -->
          <div class="rounded-xl p-3" style="background: rgba(108,92,231,0.08)">
            <p class="text-xs font-medium mb-1" style="color: var(--color-primary)">
              步骤 {{ currentStep + 1 }} / {{ totalSteps }}
            </p>
            <p class="text-sm" style="color: var(--color-text-primary)">{{ currentStepData?.description }}</p>
          </div>

          <!-- Variables State -->
          <div v-if="currentStepData?.variables" class="space-y-1.5">
            <p class="text-xs font-medium" style="color: var(--color-text-tertiary)">变量状态</p>
            <div v-for="(val, key) in currentStepData.variables" :key="key" class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-900/60">
              <span class="text-xs font-mono text-purple-300">{{ key }}</span>
              <span class="text-xs text-gray-500">=</span>
              <span class="text-xs font-mono text-amber-300">{{ JSON.stringify(val) }}</span>
            </div>
          </div>

          <!-- Visual State (Simple Array/Node representation) -->
          <div v-if="currentStepData?.visual_state?.nodes" class="mt-2">
            <p class="text-xs font-medium mb-2" style="color: var(--color-text-tertiary)">数据结构</p>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="node in currentStepData.visual_state.nodes"
                :key="node.id"
                :class="[
                  'w-14 h-14 rounded-xl flex flex-col items-center justify-center text-xs font-mono transition-all',
                  node.id === 'head' ? 'bg-purple-500/30 border border-purple-400/40' : 'bg-amber-500/20 border border-amber-400/30'
                ]"
              >
                <span class="text-purple-300">{{ node.val ?? 'H' }}</span>
                <span class="text-[10px] text-gray-500">→ {{ node.next || '∅' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Playback Controls -->
    <div v-if="result" class="glass-card !rounded-2xl p-4 mt-4">
      <div class="flex items-center justify-between">
        <button class="w-9 h-9 rounded-lg hover:bg-purple-50 flex items-center justify-center transition-colors" @click="stepBack">
          <SkipBack :size="16" style="color: var(--color-text-secondary)" />
        </button>
        <div class="flex items-center gap-2">
          <button class="w-9 h-9 rounded-lg hover:bg-purple-50 flex items-center justify-center transition-colors" @click="resetExecution">
            <RotateCcw :size="16" style="color: var(--color-text-secondary)" />
          </button>
          <button
            class="w-11 h-11 rounded-xl gradient-primary flex items-center justify-center shadow-md shadow-purple-200 active:scale-95 transition-transform"
            @click="togglePlay"
          >
            <component :is="isPlaying ? Pause : Play" :size="18" class="text-white ml-0.5" />
          </button>
          <button class="w-9 h-9 rounded-lg hover:bg-purple-50 flex items-center justify-center transition-colors" @click="stepForward">
            <SkipForward :size="16" style="color: var(--color-text-secondary)" />
          </button>
        </div>
        <span class="text-xs font-medium" style="color: var(--color-text-tertiary)">
          行 {{ currentStepData?.line || '-' }}
        </span>
      </div>
      <!-- Progress Bar -->
      <div class="w-full h-1 bg-gray-100 rounded-full mt-4 overflow-hidden">
        <div
          class="h-full gradient-primary rounded-full transition-all duration-300"
          :style="{ width: `${totalSteps ? ((currentStep + 1) / totalSteps) * 100 : 0}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.code-editor {
  background: #1a1a2e;
  min-height: 240px;
}
</style>
