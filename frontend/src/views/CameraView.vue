<script setup lang="ts">
/**
 * CameraView — 拍照识别页面（v2 视觉重设计）
 * Tab 切换：搜题模式 / 批改模式
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Search, FileCheck2, Camera, Upload, X, Sparkles, ChevronRight, AlertCircle, CheckCircle, XCircle, AlertTriangle, Lightbulb, RotateCcw, Image as ImageIcon, Clock, Zap } from 'lucide-vue-next'
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

// 滚动揭示动画（仅对 v-show 显示的元素生效）
onMounted(() => {
  // 等待 DOM 渲染
  setTimeout(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const delay = parseInt(entry.target.getAttribute('data-reveal-delay') || '0')
            setTimeout(() => {
              entry.target.classList.add('is-revealed')
            }, delay)
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -30px 0px' }
    )

    document.querySelectorAll('[data-reveal-id]').forEach((el) => {
      observer.observe(el)
    })
  }, 100)
})

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
    error.value = err?.userMessage || err?.response?.data?.detail || err?.message || (mode.value === 'search' ? '识别失败，请重试' : '分析失败，请重试')
  } finally {
    isProcessing.value = false
  }
}

function goToChat() {
  if (mode.value === 'search' && questionResult.value) {
    router.push({ path: `/chat/${questionResult.value.question_id}`, query: { subject: questionResult.value.subject } })
  } else if (mode.value === 'correction' && correctionResult.value) {
    router.push({ path: `/chat/${correctionResult.value.question_id}` })
  }
}

const modeLabel = computed(() => mode.value === 'search' ? '搜题' : '批改')
const processingText = computed(() => mode.value === 'search' ? 'AI 正在识别题目...' : 'AI 正在批改分析...')
</script>

<template>
  <div class="camera-view">
    <!-- 背景装饰：径向光晕 -->
    <div class="bg-decoration" aria-hidden="true">
      <div class="bg-glow bg-glow-1"></div>
      <div class="bg-glow bg-glow-2"></div>
    </div>

    <!-- Header -->
    <header class="camera-header" data-reveal-id="header" data-reveal-delay="0">
      <button
        class="back-btn"
        @click="router.back()"
        aria-label="返回"
      >
        <ArrowLeft :size="18" />
      </button>
      <div class="header-text">
        <h1 class="header-title">拍照识别</h1>
        <p class="header-subtitle">AI 一键识别，开启引导式学习</p>
      </div>
    </header>

    <!-- Mode Tabs -->
    <div class="mode-tabs" role="tablist" data-reveal-id="tabs" data-reveal-delay="80">
      <button
        :class="['mode-tab', { active: mode === 'search' }]"
        @click="switchMode('search')"
        role="tab"
        :aria-selected="mode === 'search'"
      >
        <Search :size="16" />
        <span>搜题</span>
        <span class="mode-hint">拍照识别题目</span>
      </button>
      <button
        :class="['mode-tab', { active: mode === 'correction' }]"
        @click="switchMode('correction')"
        role="tab"
        :aria-selected="mode === 'correction'"
      >
        <FileCheck2 :size="16" />
        <span>批改</span>
        <span class="mode-hint">分析草稿步骤</span>
      </button>
    </div>

    <!-- ===== Step 1: Upload ===== -->
    <div v-show="currentStep === 'upload'" class="step-content">
      <p class="step-hint" data-reveal-id="hint" data-reveal-delay="160">
        <Lightbulb :size="14" />
        <span>
          <template v-if="mode === 'search'">上传一道 408 考研题目照片，AI 自动识别并开始引导式讲解</template>
          <template v-else>上传草稿纸图片，AI 将逐步分析每一步计算/推导是否正确</template>
        </span>
      </p>
      <div data-reveal-id="uploader" data-reveal-delay="240">
        <ImageUploader
          v-model="uploadedImage"
          @select="onImageSelect"
          :hint="mode === 'search' ? '支持 JPG、PNG，建议拍摄清晰题目' : '拍摄清晰的草稿纸，AI 将逐步批改'"
        />
      </div>

      <!-- 特性提示卡 -->
      <div class="feature-cards">
        <div class="feature-card" data-reveal-id="f1" data-reveal-delay="320">
          <div class="feature-icon-wrap">
            <Zap :size="18" />
          </div>
          <div class="feature-text">
            <p class="feature-title">3 秒识别</p>
            <p class="feature-desc">多模态 OCR + 公式识别</p>
          </div>
        </div>
        <div class="feature-card" data-reveal-id="f2" data-reveal-delay="400">
          <div class="feature-icon-wrap">
            <Sparkles :size="18" />
          </div>
          <div class="feature-text">
            <p class="feature-title">苏格拉底引导</p>
            <p class="feature-desc">不直接给答案</p>
          </div>
        </div>
        <div class="feature-card" data-reveal-id="f3" data-reveal-delay="480">
          <div class="feature-icon-wrap">
            <Clock :size="18" />
          </div>
          <div class="feature-text">
            <p class="feature-title">24/7 在线</p>
            <p class="feature-desc">随时可用</p>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== Step 2: Preview + Confirm ===== -->
    <div v-show="currentStep === 'preview'" class="step-content">
      <div class="preview-frame">
        <ImageUploader
          v-model="uploadedImage"
          :loading="isProcessing"
          @select="onImageSelect"
          hint="确认图片清晰后点击下方按钮"
        />
      </div>
      <div class="action-group">
        <button
          :disabled="isProcessing"
          :class="['btn-primary', { 'is-loading': isProcessing }]"
          @click="startProcessing"
        >
          <Sparkles v-if="!isProcessing" :size="18" />
          <span v-else class="loading-spinner"></span>
          <span>{{ isProcessing ? processingText : (mode === 'search' ? '开始识别，进入引导讲解' : '开始批改分析') }}</span>
        </button>
        <button
          class="btn-secondary"
          @click="resetAll"
        >
          <RotateCcw :size="16" />
          <span>重新选择</span>
        </button>
      </div>
    </div>

    <!-- ===== Step 3: Result ===== -->
    <div v-show="currentStep === 'result'" class="step-content">
      <!-- Error -->
      <div v-if="error && !isProcessing" class="error-block" data-reveal-id="error" data-reveal-delay="0">
        <div class="error-icon-wrap">
          <AlertCircle :size="20" />
        </div>
        <div class="error-content">
          <p class="error-title">{{ mode === 'search' ? '识别失败' : '分析失败' }}</p>
          <p class="error-message">{{ error }}</p>
          <button class="btn-retry" @click="resetAll">
            <RotateCcw :size="14" />
            <span>重新拍照</span>
          </button>
        </div>
      </div>

      <!-- Processing -->
      <div v-if="isProcessing" class="processing-block">
        <div class="processing-orb">
          <div class="orb-ring"></div>
          <div class="orb-ring orb-ring-2"></div>
          <div class="orb-core">
            <Sparkles :size="28" />
          </div>
        </div>
        <p class="processing-title">{{ processingText }}</p>
        <p class="processing-subtitle">AI 正在分析图片内容，请稍候</p>
        <div class="processing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- ===== SEARCH RESULT ===== -->
      <template v-if="questionResult && !isProcessing && mode === 'search'">
        <div class="result-image-card" data-reveal-id="img" data-reveal-delay="0">
          <div class="result-image-label">
            <ImageIcon :size="14" />
            <span>原图</span>
          </div>
          <img :src="uploadedImage || ''" alt="原图" class="result-image" />
        </div>
        <div data-reveal-id="qcard" data-reveal-delay="100">
          <QuestionCard
            :question-id="questionResult.question_id"
            :subject="questionResult.subject"
            :knowledge-tags="questionResult.knowledge_tags"
            :difficulty="questionResult.difficulty"
            :content="questionResult.content"
          />
        </div>
        <div class="action-group" data-reveal-id="act" data-reveal-delay="200">
          <button
            class="btn-primary"
            @click="goToChat"
          >
            <span>开始引导式讲解</span>
            <ChevronRight :size="18" />
          </button>
          <button
            class="btn-secondary"
            @click="resetAll"
          >
            <RotateCcw :size="16" />
            <span>重新拍照</span>
          </button>
        </div>
      </template>

      <!-- ===== CORRECTION RESULT ===== -->
      <template v-if="correctionResult && !isProcessing && mode === 'correction'">
        <div class="result-image-card" data-reveal-id="img" data-reveal-delay="0">
          <div class="result-image-label">
            <ImageIcon :size="14" />
            <span>草稿</span>
          </div>
          <img :src="uploadedImage || ''" alt="草稿" class="result-image" />
        </div>

        <div class="correction-section" data-reveal-id="steps" data-reveal-delay="100">
          <div class="section-header">
            <h3 class="section-title">
              <FileCheck2 :size="18" />
              <span>批改结果</span>
            </h3>
            <span class="section-meta">{{ correctionResult.steps.length }} 个步骤</span>
          </div>
          <div
            v-for="(step, idx) in correctionResult.steps"
            :key="step.step_no"
            class="step-card"
            :class="step.is_correct ? 'is-correct' : 'is-wrong'"
            :data-reveal-id="`step-${idx}`"
            :data-reveal-delay="150 + idx * 80"
          >
            <div class="step-header">
              <div :class="['step-badge', step.is_correct ? 'badge-correct' : 'badge-wrong']">
                <CheckCircle v-if="step.is_correct" :size="14" />
                <XCircle v-else :size="14" />
                <span>第 {{ step.step_no }} 步</span>
              </div>
              <span v-if="step.error_type" class="error-tag">
                {{ step.error_type }}
              </span>
            </div>
            <p class="step-content-text">{{ step.content }}</p>
            <p v-if="step.hint" class="step-hint-text">
              <AlertTriangle :size="13" />
              <span>{{ step.hint }}</span>
            </p>
          </div>
        </div>

        <div class="summary-card" data-reveal-id="summary" data-reveal-delay="300">
          <div class="summary-header">
            <div class="summary-icon-wrap">
              <Lightbulb :size="18" />
            </div>
            <p class="summary-title">总体评价</p>
          </div>
          <p class="summary-text">{{ correctionResult.overall_feedback }}</p>
        </div>

        <div class="action-group" data-reveal-id="act" data-reveal-delay="400">
          <button
            class="btn-primary"
            @click="goToChat"
          >
            <span>开始引导订正</span>
            <ChevronRight :size="18" />
          </button>
          <button
            class="btn-secondary"
            @click="resetAll"
          >
            <RotateCcw :size="16" />
            <span>重新拍照</span>
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* ===========================================
   Camera View v2 — 视觉重设计
   主色：青绿 #0d9488 | 背景：极浅灰蓝 #F7F9FC
   =========================================== */

.camera-view {
  position: relative;
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 4rem;
  min-height: calc(100vh - 5rem);
}

/* 背景装饰 */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.bg-glow-1 {
  width: 500px;
  height: 500px;
  top: -100px;
  right: -100px;
  background: radial-gradient(circle, rgba(13, 148, 136, 0.12), transparent 70%);
}

.bg-glow-2 {
  width: 400px;
  height: 400px;
  bottom: 10%;
  left: -150px;
  background: radial-gradient(circle, rgba(45, 212, 191, 0.08), transparent 70%);
}

.camera-view > *:not(.bg-decoration) {
  position: relative;
  z-index: 1;
}

/* ===== Header ===== */
.camera-header {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  margin-bottom: 2rem;
  padding-top: 0.5rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border-light, #e5e7eb);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary, #4b5563);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.back-btn:hover {
  background: rgba(13, 148, 136, 0.06);
  color: #0d9488;
  border-color: rgba(13, 148, 136, 0.2);
  transform: translateX(-2px);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.header-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  letter-spacing: -0.02em;
  margin: 0;
}

.header-subtitle {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary, #6b7280);
  margin: 0;
}

/* ===== Mode Tabs ===== */
.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.375rem;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 16px;
  margin-bottom: 1.75rem;
  border: 1px solid var(--color-border-light, #e5e7eb);
}

.mode-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--color-text-muted, #6b7280);
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.mode-tab:hover {
  color: var(--color-text-secondary, #4b5563);
}

.mode-tab.active {
  background: white;
  color: #0d9488;
  box-shadow:
    0 1px 3px rgba(13, 148, 136, 0.08),
    0 1px 2px rgba(0, 0, 0, 0.04);
}

.mode-tab.active::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 24px;
  height: 2px;
  background: #0d9488;
  border-radius: 2px;
}

.mode-hint {
  font-size: 0.6875rem;
  font-weight: 400;
  opacity: 0.7;
  letter-spacing: 0.02em;
}

/* ===== Step Content ===== */
.step-content {
  animation: fadeInUp 0.4s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.step-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.05), rgba(45, 212, 191, 0.03));
  border: 1px solid rgba(13, 148, 136, 0.12);
  border-radius: 12px;
  font-size: 0.8125rem;
  color: #0f766e;
  line-height: 1.5;
}

.step-hint svg {
  flex-shrink: 0;
  color: #0d9488;
}

/* ===== Preview Frame ===== */
.preview-frame {
  position: relative;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 24px -8px rgba(13, 148, 136, 0.15);
  background: white;
  padding: 0.5rem;
}

/* ===== Action Group ===== */
.action-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 14px;
  border: none;
  background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
  color: white;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow:
    0 4px 14px rgba(13, 148, 136, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  letter-spacing: 0.01em;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow:
    0 6px 20px rgba(13, 148, 136, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-primary:disabled,
.btn-primary.is-loading {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1.5rem;
  border-radius: 14px;
  background: transparent;
  color: var(--color-text-secondary, #4b5563);
  font-size: 0.875rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  border: 1px solid var(--color-border-light, #e5e7eb);
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--color-bg-secondary, #f3f4f6);
  border-color: var(--color-border-default, #d1d5db);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== Feature Cards ===== */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 1rem 0.75rem;
  background: white;
  border: 1px solid var(--color-border-light, #e5e7eb);
  border-radius: 14px;
  transition: all 0.2s ease;
  cursor: default;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -8px rgba(13, 148, 136, 0.15);
  border-color: rgba(13, 148, 136, 0.2);
}

.feature-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.1), rgba(45, 212, 191, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0d9488;
  margin-bottom: 0.5rem;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.feature-desc {
  font-size: 0.6875rem;
  color: var(--color-text-tertiary, #6b7280);
  margin: 0;
}

/* ===== Error Block ===== */
.error-block {
  display: flex;
  gap: 0.875rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.04), rgba(239, 68, 68, 0.02));
  border: 1px solid rgba(239, 68, 68, 0.15);
  border-radius: 16px;
  margin-bottom: 1.5rem;
}

.error-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-content {
  flex: 1;
  min-width: 0;
}

.error-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #b91c1c;
  margin: 0 0 0.25rem;
}

.error-message {
  font-size: 0.8125rem;
  color: #dc2626;
  margin: 0;
  line-height: 1.5;
  opacity: 0.85;
}

.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.75rem;
  padding: 0.5rem 0.875rem;
  border-radius: 10px;
  background: white;
  color: #b91c1c;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid rgba(239, 68, 68, 0.2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-retry:hover {
  background: #fef2f2;
  border-color: rgba(239, 68, 68, 0.3);
}

/* ===== Processing Block ===== */
.processing-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 1.5rem;
  background: white;
  border: 1px solid var(--color-border-light, #e5e7eb);
  border-radius: 20px;
  margin-bottom: 1.5rem;
  box-shadow: 0 8px 24px -8px rgba(13, 148, 136, 0.1);
}

.processing-orb {
  position: relative;
  width: 88px;
  height: 88px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.orb-ring {
  position: absolute;
  inset: 0;
  border: 2px solid transparent;
  border-top-color: #0d9488;
  border-right-color: rgba(13, 148, 136, 0.3);
  border-radius: 50%;
  animation: spin 1.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) infinite;
}

.orb-ring-2 {
  inset: 8px;
  border-top-color: #14b8a6;
  border-left-color: rgba(20, 184, 166, 0.3);
  border-right-color: transparent;
  animation: spin 1s linear infinite reverse;
}

.orb-core {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.processing-title {
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0 0 0.5rem;
  text-align: center;
}

.processing-subtitle {
  font-size: 0.8125rem;
  color: var(--color-text-tertiary, #6b7280);
  margin: 0 0 1.25rem;
  text-align: center;
}

.processing-dots {
  display: flex;
  gap: 6px;
}

.processing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #0d9488;
  animation: dotBounce 1.4s ease-in-out infinite;
}

.processing-dots span:nth-child(2) { animation-delay: 0.2s; }
.processing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ===== Result Image Card ===== */
.result-image-card {
  position: relative;
  background: white;
  border: 1px solid var(--color-border-light, #e5e7eb);
  border-radius: 16px;
  padding: 0.75rem;
  margin-bottom: 1rem;
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.06);
}

.result-image-label {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: rgba(13, 148, 136, 0.1);
  color: #0d9488;
  font-size: 0.6875rem;
  font-weight: 600;
  border-radius: 999px;
  backdrop-filter: blur(4px);
  z-index: 1;
}

.result-image {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 10px;
}

/* ===== Correction Section ===== */
.correction-section {
  margin-bottom: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding: 0 0.25rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary, #111827);
  margin: 0;
}

.section-title svg {
  color: #0d9488;
}

.section-meta {
  font-size: 0.75rem;
  color: var(--color-text-tertiary, #6b7280);
  font-weight: 500;
  padding: 2px 10px;
  background: var(--color-bg-secondary, #f3f4f6);
  border-radius: 999px;
}

.step-card {
  background: white;
  border: 1px solid var(--color-border-light, #e5e7eb);
  border-radius: 14px;
  padding: 1rem 1.125rem;
  margin-bottom: 0.625rem;
  transition: all 0.2s ease;
}

.step-card:hover {
  box-shadow: 0 4px 12px -4px rgba(0, 0, 0, 0.06);
}

.step-card.is-correct {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.03), white);
  border-color: rgba(16, 185, 129, 0.2);
}

.step-card.is-wrong {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.03), white);
  border-color: rgba(239, 68, 68, 0.2);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.step-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.badge-correct {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
}

.badge-wrong {
  background: rgba(239, 68, 68, 0.1);
  color: #dc2626;
}

.error-tag {
  font-size: 0.6875rem;
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border-radius: 6px;
  font-weight: 500;
}

.step-content-text {
  font-size: 0.875rem;
  color: var(--color-text-primary, #111827);
  line-height: 1.6;
  margin: 0 0 0.5rem;
}

.step-hint-text {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin: 0;
  padding: 0.5rem 0.75rem;
  background: rgba(245, 158, 11, 0.06);
  border-left: 2px solid #f59e0b;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #b45309;
  line-height: 1.5;
}

.step-hint-text svg {
  flex-shrink: 0;
  margin-top: 2px;
  color: #f59e0b;
}

/* ===== Summary Card ===== */
.summary-card {
  background: linear-gradient(135deg, rgba(13, 148, 136, 0.04), rgba(45, 212, 191, 0.02));
  border: 1px solid rgba(13, 148, 136, 0.15);
  border-radius: 16px;
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.summary-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
}

.summary-icon-wrap {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: linear-gradient(135deg, #0d9488, #14b8a6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.summary-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f766e;
  margin: 0;
}

.summary-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary, #4b5563);
  line-height: 1.7;
  margin: 0;
}

/* ===== Reveal Animations ===== */
[data-reveal-id] {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

[data-reveal-id].is-revealed {
  opacity: 1;
  transform: translateY(0);
}

/* ===== Responsive ===== */
@media (max-width: 640px) {
  .camera-view {
    padding: 1rem 1rem 3rem;
  }

  .header-title {
    font-size: 1.25rem;
  }

  .feature-cards {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .feature-card {
    flex-direction: row;
    text-align: left;
    padding: 0.75rem 1rem;
  }

  .feature-icon-wrap {
    margin-bottom: 0;
    margin-right: 0.75rem;
  }

  .feature-text {
    flex: 1;
  }

  .processing-block {
    padding: 2rem 1rem;
  }
}

@media (min-width: 1024px) {
  .camera-view {
    padding-top: 2.5rem;
  }
}
</style>
