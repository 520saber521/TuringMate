<script setup lang="ts">
/**
 * PhotoSearchView - 拍照搜题页面
 * 完整流程：上传图片 → 预览 → AI识别 → 展示题目卡片 → 跳转引导对话
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Sparkles, ChevronRight, AlertCircle } from 'lucide-vue-next'
import ImageUploader from '@/components/upload/ImageUploader.vue'
import QuestionCard from '@/components/question/QuestionCard.vue'
import { parseQuestionImage, type QuestionParseResult } from '@/api/question'

const router = useRouter()

// 状态
const uploadedImage = ref<string | null>(null)
const selectedFile = ref<File | null>(null)
const isProcessing = ref(false)
const parseError = ref<string | null>(null)
const parseResult = ref<QuestionParseResult | null>(null)

/** 步骤：upload(上传) → preview(预览) → result(识别结果) */
type Step = 'upload' | 'preview' | 'result'
const currentStep = ref<Step>('upload')

// ImageUploader 事件
function onImageSelect(file: File) {
  selectedFile.value = file
  currentStep.value = 'preview'
  parseResult.value = null
  parseError.value = null
}

function onImageRemove() {
  uploadedImage.value = null
  selectedFile.value = null
  currentStep.value = 'upload'
}

/** 调用后端 API 识别题目 */
async function startRecognition() {
  if (!selectedFile.value) return

  isProcessing.value = true
  parseError.value = null
  currentStep.value = 'result'

  try {
    const result = await parseQuestionImage(selectedFile.value)
    console.log('[PhotoSearch] 识别成功:', result)
    parseResult.value = result
  } catch (err: any) {
    console.error('[PhotoSearch] 识别失败:', err)
    parseError.value = err?.response?.data?.detail || err?.message || '网络错误，请重试'
  } finally {
    isProcessing.value = false
  }
}

/** 跳转到引导对话页 */
function startGuidedChat() {
  if (!parseResult.value?.question_id) return
  router.push({
    path: '/chat',
    query: {
      questionId: parseResult.value.question_id,
      subject: parseResult.value.subject,
    },
  })
}

/** 重新拍照 */
function retakePhoto() {
  onImageRemove()
}
</script>

<template>
  <div class="photo-search-view animate-fade-in-up min-h-[calc(100vh-8rem)] lg:min-h-[calc(100vh-5rem)] pb-4">
    <!-- Header -->
    <header class="flex items-center gap-3 mb-6">
      <button
        class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors"
        @click="router.back()"
      >
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">拍照搜题</h2>
    </header>

    <!-- ===== Step 1/3: 上传区 ===== -->
    <div v-show="currentStep === 'upload'" class="transition-all">
      <p class="text-sm mb-4 text-center" style="color: var(--color-text-tertiary)">
        上传一张408考研题目照片，AI 将自动识别并开始引导式讲解
      </p>

      <ImageUploader
        v-model="uploadedImage"
        @select="onImageSelect"
        hint="支持 JPG、PNG 格式，建议拍摄清晰、无遮挡的题目"
      />
    </div>

    <!-- ===== Step 2/3: 图片预览 + 确认按钮 ===== -->
    <div v-show="currentStep === 'preview'" class="space-y-4 transition-all">
      <ImageUploader
        v-model="uploadedImage"
        :loading="isProcessing"
        @select="onImageSelect"
        hint="确认图片清晰后点击下方按钮开始识别"
      />

      <button
        :disabled="isProcessing"
        :class="[
          'w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 transition-all',
          isProcessing
            ? 'bg-purple-300 cursor-not-allowed'
            : 'gradient-primary shadow-lg shadow-purple-200 active:scale-[0.98]',
        ]"
        @click="startRecognition"
      >
        <component :is="isProcessing ? Sparkles : 'span'" :size="18">
          <template v-if="!isProcessing">✨</template>
        </component>
        {{ isProcessing ? 'AI 正在识别题目...' : '开始识别，进入引导讲解' }}
      </button>

      <p class="text-xs text-center" style="color: var(--color-text-tertiary)">
        AI 将自动分析科目、知识点、难度，然后开始苏格拉底式引导讲解
      </p>
    </div>

    <!-- ===== Step 3/3: 识别结果 + 题目卡片 + 跳转 ===== -->
    <div v-show="currentStep === 'result'" class="space-y-4 transition-all">
      <!-- 错误状态 -->
      <div v-if="parseError && !isProcessing" class="error-card glass-card !rounded-2xl p-5 flex items-start gap-3 border border-red-100 bg-red-50/50">
        <AlertCircle :size="20" class="text-red-500 shrink-0 mt-0.5" />
        <div>
          <p class="font-medium text-red-700 text-sm mb-1">识别失败</p>
          <p class="text-red-600 text-xs leading-relaxed">{{ parseError }}</p>
          <button class="mt-3 px-4 py-1.5 rounded-lg bg-red-100 text-red-600 text-xs font-medium hover:bg-red-200 transition-colors" @click="retakePhoto">
            重新拍照
          </button>
        </div>
      </div>

      <!-- 处理中 -->
      <div v-if="isProcessing" class="processing-card glass-card !rounded-2xl p-8 flex flex-col items-center justify-center">
        <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-4">
          <Sparkles :size="24" class="text-purple-500 animate-pulse" />
        </div>
        <p class="font-semibold text-base mb-1" style="color: var(--color-text-primary)">正在识别题目...</p>
        <p class="text-xs" style="color: var(--color-text-tertiary)">AI 正在分析图片内容，请稍候</p>
      </div>

      <!-- 识别成功 - 题目卡片 + 操作按钮 -->
      <template v-if="parseResult && !isProcessing">
        <!-- 缩略图预览 -->
        <div class="glass-card !rounded-2xl p-3 overflow-hidden">
          <img :src="uploadedImage || ''" alt="原图" class="w-full max-h-[180px] object-contain rounded-lg" />
        </div>

        <!-- 题目信息卡片 -->
        <QuestionCard
          :question-id="parseResult.question_id"
          :subject="parseResult.subject"
          :knowledge-tags="parseResult.knowledge_tags"
          :difficulty="parseResult.difficulty"
          :content="parseResult.content"
          :image-url="undefined"
        />

        <!-- 操作按钮组 -->
        <div class="space-y-3">
          <button
            class="w-full py-3.5 rounded-xl gradient-primary text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-purple-200 active:scale-[0.98] transition-all hover:shadow-purple-300"
            @click="startGuidedChat"
          >
            开始引导式讲解
            <ChevronRight :size="18" />
          </button>

          <div class="flex gap-3">
            <button
              class="flex-1 py-2.5 rounded-xl border border-gray-200 text-sm font-medium flex items-center justify-center gap-1.5 hover:bg-gray-50 transition-colors"
              style="color: var(--color-text-secondary)"
              @click="retakePhoto"
            >
              重新拍照
            </button>
            <button
              class="flex-1 py-2.5 rounded-xl border border-purple-200 text-sm font-medium flex items-center justify-center gap-1.5 text-purple-600 hover:bg-purple-50 transition-colors"
            >
              编辑题面
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.error-card { animation: shake 0.4s ease-in-out; }

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-6px); }
  75% { transform: translateX(6px); }
}

.processing-card { animation: fadeInUp 0.3s ease; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
