<script setup lang="ts">
/**
 * CameraView — 统一拍照识别页面
 * Tab 切换：搜题模式 / 批改模式
 */
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Sparkles, ChevronRight, AlertCircle, CheckCircle, XCircle, AlertTriangle } from 'lucide-vue-next'
import ImageUploader from '@/components/upload/ImageUploader.vue'
import QuestionCard from '@/components/question/QuestionCard.vue'
import { parseQuestionImage, type QuestionParseResult } from '@/api/question'
import { analyzeCorrection, type CorrectionResult } from '@/api/correction'

const router = useRouter()

type Mode = 'search' | 'correction'
const mode = ref<Mode>('search')

const uploadedImage = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const isProcessing = ref(false)
const error = ref<string | null>(null)
const questionResult = ref<QuestionParseResult | null>(null)
const correctionResult = ref<CorrectionResult | null>(null)

type Step = 'upload' | 'preview' | 'result'
const currentStep = ref<Step>('upload')

function switchMode(m: Mode) {
  if (m === mode.value) return
  mode.value = m
  resetAll()
}

function resetAll() {
  uploadedImage.value = null
  selectedFile.value = null
  currentStep.value = 'upload'
  questionResult.value = null
  correctionResult.value = null
  error.value = null
  isProcessing.value = false
}

function onImageSelect(file: File) {
  selectedFile.value = file
  currentStep.value = 'preview'
  questionResult.value = null
  correctionResult.value = null
  error.value = null
}

async function startProcessing() {
  if (!selectedFile.value) return

  isProcessing.value = true
  error.value = null
  currentStep.value = 'result'

  try {
    if (mode.value === 'search') {
      questionResult.value = await parseQuestionImage(selectedFile.value)
    } else {
      correctionResult.value = await analyzeCorrection(selectedFile.value)
    }
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || (mode.value === 'search' ? '识别失败，请重试' : '分析失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

function goToChat() {
  if (mode.value === 'search' && questionResult.value) {
    router.push({ path: '/chat', query: { questionId: questionResult.value.question_id, subject: questionResult.value.subject } })
  } else if (mode.value === 'correction' && correctionResult.value) {
    router.push({ path: '/chat', query: { questionId: correctionResult.value.question_id } })
  }
}

const modeLabel = computed(() => mode.value === 'search' ? '搜题' : '批改')
const processingText = computed(() => mode.value === 'search' ? 'AI 正在识别题目...' : 'AI 正在批改分析...')
</script>

<template>
  <div class="camera-view animate-fade-in-up min-h-[calc(100vh-8rem)] lg:min-h-[calc(100vh-5rem)] pb-4">
    <!-- Header -->
    <header class="flex items-center gap-3 mb-6">
      <button
        class="w-10 h-10 rounded-xl hover:bg-amber-50 flex items-center justify-center transition-colors"
        @click="router.back()"
      >
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">拍照识别</h2>
    </header>

    <!-- Mode Tabs -->
    <div class="camera-tabs mb-5">
      <button
        :class="['camera-tab', { active: mode === 'search' }]"
        @click="switchMode('search')"
      >
        <span>搜题</span>
      </button>
      <button
        :class="['camera-tab', { active: mode === 'correction' }]"
        @click="switchMode('correction')"
      >
        <span>批改</span>
      </button>
    </div>

    <!-- ===== Step 1: Upload ===== -->
    <div v-show="currentStep === 'upload'" class="transition-all">
      <p class="text-sm mb-4 text-center" style="color: var(--color-text-tertiary)">
        <template v-if="mode === 'search'">上传一道 408 考研题目照片，AI 自动识别并开始引导式讲解</template>
        <template v-else>上传草稿纸图片，AI 将逐步分析每一步计算/推导是否正确</template>
      </p>
      <ImageUploader
        v-model="uploadedImage"
        @select="onImageSelect"
        :hint="mode === 'search' ? '支持 JPG、PNG，建议拍摄清晰题目' : '拍摄清晰的草稿纸，AI 将逐步批改'"
      />
    </div>

    <!-- ===== Step 2: Preview + Confirm ===== -->
    <div v-show="currentStep === 'preview'" class="space-y-4 transition-all">
      <ImageUploader
        v-model="uploadedImage"
        :loading="isProcessing"
        @select="onImageSelect"
        hint="确认图片清晰后点击下方按钮"
      />
      <button
        :disabled="isProcessing"
        :class="[
          'w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 transition-all',
          isProcessing
            ? 'cursor-not-allowed opacity-50'
            : 'active:scale-[0.98] shadow-lg',
        ]"
        style="background: linear-gradient(135deg, #7c3aed, #6d28d9); --tw-shadow-color: rgba(124, 58, 237, 0.25);"
        @click="startProcessing"
      >
        <Sparkles :size="18" />
        {{ isProcessing ? processingText : (mode === 'search' ? '开始识别，进入引导讲解' : '开始批改分析') }}
      </button>
    </div>

    <!-- ===== Step 3: Result ===== -->
    <div v-show="currentStep === 'result'" class="space-y-4 transition-all">
      <!-- Error -->
      <div v-if="error && !isProcessing" class="rounded-xl p-5 bg-red-50/80 border border-red-100 text-sm text-red-600 flex items-start gap-3">
        <AlertCircle :size="20" class="text-red-500 shrink-0 mt-0.5" />
        <div>
          <p class="font-medium mb-1">{{ mode === 'search' ? '识别失败' : '分析失败' }}</p>
          <p class="text-xs leading-relaxed">{{ error }}</p>
          <button class="mt-3 px-4 py-1.5 rounded-lg bg-red-100 text-red-600 text-xs font-medium hover:bg-red-200 transition-colors" @click="resetAll">
            重新拍照
          </button>
        </div>
      </div>

      <!-- Processing -->
      <div v-if="isProcessing" class="glass-card !rounded-2xl p-8 flex flex-col items-center justify-center">
        <div class="w-12 h-12 rounded-full flex items-center justify-center mb-4" style="background: rgba(124, 58, 237, 0.1);">
          <Sparkles :size="24" class="animate-pulse" style="color: var(--color-primary-500)" />
        </div>
        <p class="font-semibold text-base mb-1" style="color: var(--color-text-primary)">{{ processingText }}</p>
        <p class="text-xs" style="color: var(--color-text-tertiary)">AI 正在分析图片内容，请稍候</p>
      </div>

      <!-- ===== SEARCH RESULT ===== -->
      <template v-if="questionResult && !isProcessing && mode === 'search'">
        <div class="glass-card !rounded-2xl p-3 overflow-hidden">
          <img :src="uploadedImage || ''" alt="原图" class="w-full max-h-[180px] object-contain rounded-lg" />
        </div>
        <QuestionCard
          :question-id="questionResult.question_id"
          :subject="questionResult.subject"
          :knowledge-tags="questionResult.knowledge_tags"
          :difficulty="questionResult.difficulty"
          :content="questionResult.content"
        />
        <div class="space-y-3">
          <button
            class="w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 shadow-lg active:scale-[0.98] transition-all"
            style="background: linear-gradient(135deg, #7c3aed, #6d28d9);"
            @click="goToChat"
          >
            开始引导式讲解
            <ChevronRight :size="18" />
          </button>
          <button
            class="w-full py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors"
            @click="resetAll"
          >
            重新拍照
          </button>
        </div>
      </template>

      <!-- ===== CORRECTION RESULT ===== -->
      <template v-if="correctionResult && !isProcessing && mode === 'correction'">
        <div class="glass-card !rounded-2xl p-3 overflow-hidden">
          <img :src="uploadedImage || ''" alt="草稿" class="w-full max-h-[200px] object-contain rounded-lg" />
        </div>

        <div class="space-y-3">
          <h3 class="text-base font-semibold" style="color: var(--color-text-primary)">批改结果</h3>
          <div
            v-for="step in correctionResult.steps"
            :key="step.step_no"
            :class="[
              'rounded-xl p-4 border',
              step.is_correct
                ? 'bg-emerald-50/50 border-emerald-100'
                : 'bg-red-50/50 border-red-100'
            ]"
          >
            <div class="flex items-start gap-3">
              <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', step.is_correct ? 'bg-emerald-100' : 'bg-red-100']">
                <CheckCircle v-if="step.is_correct" :size="18" class="text-emerald-500" />
                <XCircle v-else :size="18" class="text-red-500" />
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span class="text-xs font-semibold" :style="{ color: step.is_correct ? '#10B981' : '#EF4444' }">
                    第 {{ step.step_no }} 步
                  </span>
                  <span v-if="step.error_type" class="px-2 py-0.5 rounded-md text-xs font-medium bg-red-100 text-red-600">
                    {{ step.error_type }}
                  </span>
                </div>
                <p class="text-sm" style="color: var(--color-text-primary)">{{ step.content }}</p>
                <p v-if="step.hint" class="text-xs mt-2 text-amber-600 flex items-start gap-1">
                  <AlertTriangle :size="12" class="mt-0.5 flex-shrink-0" />
                  {{ step.hint }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div class="glass-card !rounded-2xl p-4">
          <p class="text-sm font-medium mb-2" style="color: var(--color-text-primary)">总体评价</p>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-secondary)">{{ correctionResult.overall_feedback }}</p>
        </div>

        <div class="space-y-3">
          <button
            class="w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 shadow-lg active:scale-[0.98] transition-all"
            style="background: linear-gradient(135deg, #7c3aed, #6d28d9);"
            @click="goToChat"
          >
            开始引导订正
            <ChevronRight :size="18" />
          </button>
          <button
            class="w-full py-2.5 rounded-xl border border-gray-200 text-sm font-medium text-text-secondary hover:bg-gray-50 transition-colors"
            @click="resetAll"
          >
            重新拍照
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* Mode Tabs */
.camera-tabs {
  display: flex;
  gap: 0.5rem;
  padding: 0.35rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
}

.camera-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.camera-tab:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-primary);
}

.camera-tab.active {
  background: white;
  color: var(--color-primary-600);
  font-weight: 600;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(0, 0, 0, 0.04);
}
</style>
