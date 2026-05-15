<script setup lang="ts">
/**
 * CorrectionView - 手写批改页面
 * 上传草稿纸 → AI 批改分析 → 展示每步判断 → 引导订正
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Camera, Upload, PenTool, ChevronRight, CheckCircle, XCircle, AlertTriangle } from 'lucide-vue-next'
import ImageUploader from '@/components/upload/ImageUploader.vue'
import { analyzeCorrection, type CorrectionStep, type CorrectionResult } from '@/api/correction'

const router = useRouter()

const uploadedImage = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const isProcessing = ref(false)
const error = ref<string | null>(null)
const result = ref<CorrectionResult | null>(null)

type Step = 'upload' | 'preview' | 'result'
const currentStep = ref<Step>('upload')

function onImageSelect(file: File) {
  selectedFile.value = file
  currentStep.value = 'preview'
  result.value = null
  error.value = null
}

function onImageRemove() {
  uploadedImage.value = null
  selectedFile.value = null
  currentStep.value = 'upload'
  result.value = null
}

async function startAnalysis() {
  if (!selectedFile.value) return

  isProcessing.value = true
  error.value = null
  currentStep.value = 'result'

  try {
    const res = await analyzeCorrection(selectedFile.value)
    result.value = res
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || '分析失败，请重试'
  } finally {
    isProcessing.value = false
  }
}

function goToGuidedChat() {
  if (!result.value) return
  router.push({
    path: '/chat',
    query: { questionId: result.value.question_id },
  })
}

function retakePhoto() {
  onImageRemove()
}
</script>

<template>
  <div class="correction-view animate-fade-in-up pb-20 lg:pb-0">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors" @click="router.back()">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">手写批改</h2>
    </div>

    <!-- Step 1: Upload -->
    <div v-show="currentStep === 'upload'">
      <p class="text-sm mb-4 text-center" style="color: var(--color-text-tertiary)">
        上传草稿纸图片，AI 将分析每一步计算/推导是否正确
      </p>
      <ImageUploader
        v-model="uploadedImage"
        @select="onImageSelect"
        hint="拍摄清晰的草稿纸，AI 将逐步批改"
      />
    </div>

    <!-- Step 2: Preview + Confirm -->
    <div v-show="currentStep === 'preview'" class="space-y-4">
      <ImageUploader
        v-model="uploadedImage"
        :loading="isProcessing"
        @select="onImageSelect"
        hint="确认图片清晰后点击下方按钮开始批改"
      />
      <button
        :disabled="isProcessing"
        :class="[
          'w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 transition-all',
          isProcessing
            ? 'bg-emerald-300 cursor-not-allowed'
            : 'active:scale-[0.98] shadow-lg shadow-emerald-200',
        ]"
        style="background: linear-gradient(135deg, #10B981 0%, #059669 100%)"
        @click="startAnalysis"
      >
        <PenTool :size="18" />
        {{ isProcessing ? 'AI 正在批改...' : '开始批改分析' }}
      </button>
    </div>

    <!-- Step 3: Results -->
    <div v-show="currentStep === 'result'" class="space-y-4">
      <!-- Error -->
      <div v-if="error && !isProcessing" class="rounded-xl p-4 bg-red-50/80 border border-red-100 text-sm text-red-600">
        <p class="font-medium mb-1">分析失败</p>
        <p class="text-xs">{{ error }}</p>
        <button class="mt-2 px-3 py-1.5 rounded-lg bg-red-100 text-red-600 text-xs font-medium hover:bg-red-200 transition-colors" @click="retakePhoto">
          重新拍照
        </button>
      </div>

      <!-- Processing -->
      <div v-if="isProcessing" class="glass-card !rounded-2xl p-8 flex flex-col items-center justify-center">
        <div class="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center mb-4">
          <PenTool :size="24" class="text-emerald-500 animate-pulse" />
        </div>
        <p class="font-semibold text-base mb-1" style="color: var(--color-text-primary)">正在批改分析...</p>
        <p class="text-xs" style="color: var(--color-text-tertiary)">AI 正在识别手写步骤并判断正误</p>
      </div>

      <!-- Results Display -->
      <template v-if="result && !isProcessing">
        <!-- Original Image -->
        <div class="glass-card !rounded-2xl p-3 overflow-hidden">
          <img :src="uploadedImage || ''" alt="草稿" class="w-full max-h-[200px] object-contain rounded-lg" />
        </div>

        <!-- Steps List -->
        <div class="space-y-3">
          <h3 class="text-base font-semibold" style="color: var(--color-text-primary)">批改结果</h3>

          <div
            v-for="step in result.steps"
            :key="step.step_no"
            :class="[
              'rounded-xl p-4 border',
              step.is_correct
                ? 'bg-emerald-50/50 border-emerald-100'
                : 'bg-red-50/50 border-red-100'
            ]"
          >
            <div class="flex items-start gap-3">
              <!-- Status Icon -->
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

        <!-- Overall Feedback -->
        <div class="glass-card !rounded-2xl p-4">
          <p class="text-sm font-medium mb-2" style="color: var(--color-text-primary)">总体评价</p>
          <p class="text-sm leading-relaxed" style="color: var(--color-text-secondary)">{{ result.overall_feedback }}</p>
        </div>

        <!-- Action Buttons -->
        <div class="space-y-3">
          <button
            class="w-full py-3.5 rounded-xl gradient-primary text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-purple-200 active:scale-[0.98] transition-all"
            @click="goToGuidedChat"
          >
            开始引导订正
            <ChevronRight :size="18" />
          </button>
          <button
            class="w-full py-2.5 rounded-xl border border-gray-200 text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-gray-50 transition-colors"
            style="color: var(--color-text-secondary)"
            @click="retakePhoto"
          >
            重新拍照
          </button>
        </div>
      </template>
    </div>
  </div>
</template>
