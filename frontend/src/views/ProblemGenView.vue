<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Sparkles, ArrowRight, CheckCircle, XCircle, AlertCircle, Loader2, BookOpen, Lightbulb } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import TopicTag from '@/components/question/TopicTag.vue'
import { generateVariants, validateAnswer, getTemplates } from '@/api/problemGen'
import type { VariantQuestion, Template, ValidateResponse } from '@/api/problemGen'

const router = useRouter()

// State machine: select -> generating -> answering -> validating -> result
type Stage = 'select' | 'generating' | 'answering' | 'validating' | 'result'
const stage = ref<Stage>('select')
const errorMsg = ref('')

// Subject & knowledge point selection
const subjects = ['数据结构', '计算机组成原理', '操作系统', '计算机网络']
const selectedSubject = ref('数据结构')
const knowledgeInput = ref('')
const knowledgeTags = ref<string[]>([])
const difficulty = ref(3)
const sourceQuestion = ref('')

// Templates
const templates = ref<Template[]>([])

// Generated content
const sourceQ = ref<VariantQuestion | null>(null)
const variants = ref<VariantQuestion[]>([])
const currentVariantIndex = ref(0)
const userAnswer = ref('')

// Result
const validateResult = ref<ValidateResponse | null>(null)

const currentVariant = computed(() => variants.value[currentVariantIndex.value])
const totalVariants = computed(() => variants.value.length)

function addTag() {
  const tag = knowledgeInput.value.trim()
  if (tag && !knowledgeTags.value.includes(tag)) {
    knowledgeTags.value.push(tag)
  }
  knowledgeInput.value = ''
}

function removeTag(tag: string) {
  knowledgeTags.value = knowledgeTags.value.filter(t => t !== tag)
}

async function handleGenerate() {
  errorMsg.value = ''
  stage.value = 'generating'
  try {
    const res = await generateVariants({
      subject: selectedSubject.value,
      knowledge_tags: knowledgeTags.value,
      difficulty: difficulty.value,
      source_question: sourceQuestion.value || undefined,
    })
    sourceQ.value = res.source_question
    variants.value = res.variants
    currentVariantIndex.value = 0
    userAnswer.value = ''
    validateResult.value = null
    stage.value = 'answering'
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '生成变式题失败'
    stage.value = 'select'
  }
}

async function handleSubmit() {
  if (!userAnswer.value.trim()) return
  errorMsg.value = ''
  stage.value = 'validating'
  try {
    const res = await validateAnswer({
      variant_id: currentVariant.value!.id,
      user_answer: userAnswer.value,
    })
    validateResult.value = res
    stage.value = 'result'
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '验证失败'
    stage.value = 'answering'
  }
}

function nextVariant() {
  if (currentVariantIndex.value < variants.value.length - 1) {
    currentVariantIndex.value++
    userAnswer.value = ''
    validateResult.value = null
    stage.value = 'answering'
  }
}

function handleReset() {
  stage.value = 'select'
  variants.value = []
  sourceQ.value = null
  validateResult.value = null
  userAnswer.value = ''
}

async function loadTemplates() {
  try {
    templates.value = await getTemplates()
  } catch { /* ignore */ }
}

loadTemplates()

const masteryIcon = computed(() => {
  if (!validateResult.value) return null
  switch (validateResult.value.mastery_level) {
    case '已掌握': return CheckCircle
    case '部分掌握': return AlertCircle
    case '未掌握': return XCircle
  }
})

const masteryColor = computed(() => {
  if (!validateResult.value) return ''
  switch (validateResult.value.mastery_level) {
    case '已掌握': return 'var(--color-success-500, #10b981)'
    case '部分掌握': return 'var(--color-warning-500, #f59e0b)'
    case '未掌握': return 'var(--color-danger-500, #ef4444)'
  }
})
</script>

<template>
  <div class="problem-gen-page">
    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>

    <!-- Stage: Select -->
    <div v-if="stage === 'select'" class="select-stage">
      <div class="pg-intro">
        <p class="pg-intro__overline font-serif">变式题生成器</p>
        <h1 class="pg-intro__title">举一反三，触类旁通</h1>
        <p class="pg-intro__desc">掌握一道题背后的知识点，比刷一百道题更重要</p>
      </div>

      <div class="config-card surface-paper">
        <h2 class="config-card__title">配置变式题</h2>
        <div class="form-grid">
          <div class="form-field">
            <label class="field-label">科目</label>
            <div class="subject-chips">
              <button
                v-for="s in subjects" :key="s"
                :class="['chip', { active: selectedSubject === s }]"
                @click="selectedSubject = s"
              >{{ s }}</button>
            </div>
          </div>
          <div class="form-field">
            <label class="field-label">知识点标签</label>
            <div class="tag-input-row">
              <div class="tags-display">
                <TopicTag v-for="t in knowledgeTags" :key="t" :label="t" variant="filled" />
              </div>
              <input
                v-model="knowledgeInput"
                class="tag-input"
                placeholder="输入知识点，回车添加"
                @keyup.enter="addTag"
              />
            </div>
          </div>
          <div class="form-field">
            <label class="field-label">难度</label>
            <div class="difficulty-row">
              <button
                v-for="n in 5" :key="n"
                :class="['diff-btn', { active: difficulty >= n }]"
                :aria-label="'难度 ' + n"
                @click="difficulty = n"
              >
                <span class="diff-btn__num">{{ n }}</span>
                <span class="diff-btn__star">&#9733;</span>
              </button>
            </div>
          </div>
          <div class="form-field">
            <label class="field-label">原题 <span class="field-label__hint">选填</span></label>
            <textarea
              v-model="sourceQuestion"
              class="field-textarea"
              rows="3"
              placeholder="粘贴原题内容，不填则基于知识点自动出题"
            ></textarea>
          </div>
        </div>
        <Button variant="primary" size="lg" class="generate-btn" @click="handleGenerate">
          <Sparkles :size="18" />
          生成变式题
        </Button>
      </div>

      <!-- Templates -->
      <div v-if="templates.length" class="templates-card surface-paper">
        <h2 class="templates-card__title">内置模板</h2>
        <div class="template-grid">
          <div v-for="t in templates.slice(0, 8)" :key="t.id" class="template-item">
            <Badge :variant="t.subject === '数据结构' ? 'primary' : t.subject === '操作系统' ? 'success' : t.subject === '计算机组成原理' ? 'warning' : 'amber'" size="sm">
              {{ t.subject }}
            </Badge>
            <span class="template-topic">{{ t.topic }}</span>
            <span class="template-diff">难度 {{ t.difficulty }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Stage: Generating -->
    <div v-if="stage === 'generating'" class="loading-stage">
      <div class="loading-card">
        <div class="loading-spinner">
          <Loader2 :size="40" class="spinning" />
        </div>
        <p class="loading-text">正在生成变式题...</p>
        <p class="loading-hint">基于「{{ selectedSubject }}」· {{ knowledgeTags.join('、') || '综合知识点' }}</p>
      </div>
    </div>

    <!-- Stage: Answering / Validating / Result -->
    <div v-if="stage === 'answering' || stage === 'validating' || stage === 'result'" class="practice-stage">
      <div class="practice-topbar">
        <button class="practice-back" @click="handleReset" aria-label="返回配置">
          <ArrowRight :size="16" class="rotate-180" />
        </button>
        <div class="variant-progress">
          <span class="progress-label">变式题 {{ currentVariantIndex + 1 }} / {{ totalVariants }}</span>
          <div class="progress-bar-track">
            <div class="progress-bar-fill" :style="{ width: `${((currentVariantIndex + 1) / totalVariants) * 100}%` }"></div>
          </div>
        </div>
      </div>

      <div class="practice-layout">
        <!-- Source Question -->
        <div v-if="sourceQ" class="source-card surface-paper">
          <div class="source-label">原题</div>
          <p class="source-content">{{ sourceQ.content }}</p>
          <div class="source-tags">
            <TopicTag v-for="t in sourceQ.knowledge_tags" :key="t" :label="t" variant="outline" />
          </div>
        </div>

        <!-- Current Variant -->
        <div v-if="currentVariant" class="variant-card surface-paper">
          <div class="variant-header">
            <Badge variant="primary">{{ currentVariant.subject }}</Badge>
            <Badge variant="amber">难度 {{ currentVariant.difficulty }}</Badge>
          </div>
          <p class="variant-content">{{ currentVariant.content }}</p>
          <div class="variant-tags">
            <TopicTag v-for="t in currentVariant.knowledge_tags" :key="t" :label="t" variant="outline" />
          </div>

          <!-- Answer input -->
          <div v-if="stage === 'answering'" class="answer-section">
            <label class="field-label" for="variant-answer">你的答案</label>
            <textarea
              id="variant-answer"
              v-model="userAnswer"
              class="answer-input"
              rows="5"
              placeholder="在此作答，写出你的推导过程..."
            ></textarea>
            <div class="answer-actions">
              <Button variant="primary" :disabled="!userAnswer.trim()" @click="handleSubmit">
                提交验证
                <ArrowRight :size="16" />
              </Button>
            </div>
          </div>

          <!-- Validating -->
          <div v-if="stage === 'validating'" class="validating-section">
            <Loader2 :size="24" class="spinning" />
            <span>AI 正在评估你的答案...</span>
          </div>

          <!-- Result -->
          <div v-if="stage === 'result' && validateResult" class="result-section">
            <div class="result-banner" :class="'result-banner--' + validateResult.mastery_level">
              <component :is="masteryIcon" :size="32" />
              <div>
                <span class="result-level">{{ validateResult.mastery_level }}</span>
                <p class="result-feedback">{{ validateResult.feedback }}</p>
              </div>
            </div>
            <div class="result-actions">
              <Button
                v-if="currentVariantIndex < variants.length - 1"
                variant="primary"
                @click="nextVariant"
              >
                下一题
                <ArrowRight :size="16" />
              </Button>
              <Button v-else variant="secondary" @click="handleReset">
                完成 · 重新开始
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.problem-gen-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 1.5rem;
}

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
   INTRO — Workshop feel
   ============================ */
.pg-intro {
  text-align: center;
  margin-bottom: 2rem;
}
.pg-intro__overline {
  font-size: 0.88rem;
  color: var(--color-amber-600);
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
}
.pg-intro__title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.3rem;
}
.pg-intro__desc {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

/* ============================
   CONFIG CARD
   ============================ */
.config-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.config-card__title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1.25rem;
}

.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.field-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.4rem;
  display: block;
}
.field-label__hint {
  font-weight: 400;
  color: var(--color-text-muted);
  font-size: 0.78rem;
}

/* Subject chips */
.subject-chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.chip {
  padding: 0.45rem 1rem;
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}
.chip:hover {
  border-color: var(--color-border-strong);
}
.chip.active {
  border-color: var(--color-primary-400);
  background: var(--color-primary-50);
  color: var(--color-primary-600);
  font-weight: 600;
}

/* Tag input */
.tag-input-row {
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 0.5rem 0.7rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
  background: var(--color-bg-primary);
  transition: border-color var(--transition-fast);
}
.tag-input-row:focus-within {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-border-focus);
}
.tags-display {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
}
.tag-input {
  border: none;
  outline: none;
  flex: 1;
  min-width: 120px;
  font-size: 0.85rem;
  color: var(--color-text-primary);
  background: transparent;
  font-family: inherit;
}

/* Difficulty */
.difficulty-row {
  display: flex;
  gap: 0.5rem;
}
.diff-btn {
  width: 42px;
  height: 42px;
  border-radius: var(--radius-md);
  border: 1.5px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1px;
  font-family: inherit;
}
.diff-btn:hover {
  border-color: var(--color-amber-300);
  color: var(--color-amber-600);
}
.diff-btn.active {
  border-color: var(--color-amber-400);
  background: var(--color-bg-glow);
  color: var(--color-amber-600);
  box-shadow: 0 0 12px rgba(245, 158, 11, 0.12);
}
.diff-btn__num {
  font-size: 0.85rem;
  font-weight: 700;
  line-height: 1;
}
.diff-btn__star {
  font-size: 0.5rem;
  opacity: 0.5;
  line-height: 1;
}
.diff-btn.active .diff-btn__star {
  opacity: 1;
  color: var(--color-amber-400);
}

/* Textarea */
.field-textarea,
.answer-input {
  width: 100%;
  padding: 0.75rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  color: var(--color-text-primary);
  background: var(--color-bg-primary);
  outline: none;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color var(--transition-fast);
  line-height: 1.6;
}
.field-textarea:focus,
.answer-input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-border-focus);
}

.generate-btn {
  margin-top: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Templates */
.templates-card {
  padding: 1.25rem;
}
.templates-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.8rem;
}
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.5rem;
}
.template-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.75rem;
  border-radius: var(--radius-sm);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
}
.template-topic {
  font-size: 0.84rem;
  color: var(--color-text-primary);
  font-weight: 500;
  flex: 1;
}
.template-diff {
  font-size: 0.73rem;
  color: var(--color-text-muted);
}

/* ============================
   LOADING
   ============================ */
.loading-stage {
  display: flex;
  justify-content: center;
  padding: 5rem 0;
}
.loading-card {
  text-align: center;
}
.loading-spinner {
  margin-bottom: 1.25rem;
  color: var(--color-primary-500);
}
.spinning {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.3rem;
}
.loading-hint {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

/* ============================
   PRACTICE STAGE
   ============================ */
.practice-topbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.practice-back {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-bg-primary);
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.practice-back:hover {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}
.rotate-180 {
  transform: rotate(180deg);
}

.variant-progress {
  flex: 1;
}
.progress-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-bottom: 0.3rem;
  display: block;
}
.progress-bar-track {
  height: 6px;
  background: var(--color-border-light);
  border-radius: 3px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary-400), var(--color-amber-400));
  border-radius: 3px;
  transition: width 0.5s cubic-bezier(0.22, 1, 0.36, 1);
}

.practice-layout {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Source card */
.source-card {
  padding: 1rem 1.25rem;
  opacity: 0.8;
}
.source-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.5rem;
}
.source-content {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
}
.source-tags {
  display: flex;
  gap: 0.3rem;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}

/* Variant card */
.variant-card {
  padding: 1.5rem;
}
.variant-header {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 1rem;
}
.variant-content {
  font-size: 1.02rem;
  color: var(--color-text-primary);
  line-height: 1.7;
  font-weight: 500;
}
.variant-tags {
  display: flex;
  gap: 0.3rem;
  margin-top: 0.8rem;
  flex-wrap: wrap;
}

/* Answer */
.answer-section {
  margin-top: 1.5rem;
  border-top: 1px solid var(--color-border-light);
  padding-top: 1.25rem;
}
.answer-actions {
  margin-top: 0.8rem;
  display: flex;
  justify-content: flex-end;
}

/* Validating */
.validating-section {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-top: 1.5rem;
  padding: 1.25rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  justify-content: center;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}
.validating-section .spinning {
  color: var(--color-primary-500);
}

/* Result */
.result-section {
  margin-top: 1.5rem;
  border-top: 1px solid var(--color-border-light);
  padding-top: 1.25rem;
}
.result-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  padding: 1rem 1.2rem;
  border-radius: var(--radius-lg);
  margin-bottom: 1rem;
}
.result-banner--已掌握 {
  background: var(--color-bg-success-soft);
  color: var(--color-success-600);
}
.result-banner--部分掌握 {
  background: var(--color-bg-warning-soft);
  color: var(--color-warning-600);
}
.result-banner--未掌握 {
  background: var(--color-bg-danger-soft);
  color: var(--color-danger-600);
}
.result-level {
  font-size: 1.15rem;
  font-weight: 700;
  display: block;
  margin-bottom: 0.2rem;
}
.result-feedback {
  font-size: 0.9rem;
  line-height: 1.6;
  opacity: 0.85;
  margin: 0;
}
.result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* ============================
   RESPONSIVE
   ============================ */
@media (max-width: 640px) {
  .problem-gen-page { padding: 1rem; }
  .template-grid { grid-template-columns: 1fr; }
  .subject-chips { gap: 0.3rem; }
  .chip { padding: 0.35rem 0.7rem; font-size: 0.8rem; }
  .pg-intro__title { font-size: 1.3rem; }
  .config-card { padding: 1.2rem; }
}
</style>
