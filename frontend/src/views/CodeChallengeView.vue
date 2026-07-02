<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Code2, Play, CheckCircle2, XCircle, Clock, Zap, TrendingUp,
  ChevronRight, Loader2, BookOpen, Lightbulb, ArrowLeft, Triangle, Send
} from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { getChallenges, getChallenge, executeCode, submitAnswer, getExplanation } from '@/api/code'
import type { CodeChallenge, ExecutionResult } from '@/api/code'

type StageType = 'list' | 'detail' | 'result'
const stage = ref<StageType>('list')
const isLoading = ref(false)
const errorMsg = ref('')

const challenges = ref<CodeChallenge[]>([])
const currentChallenge = ref<CodeChallenge | null>(null)
const userCode = ref('')
const executionResult = ref<ExecutionResult | null>(null)
const explanation = ref('')
const activeTab = ref<'code'|'result'>('code')
const submitting = ref(false)
const showExplanation = ref(false)

const filters = ref({ subject: '', type: '', difficulty: '' })

const subjectOptions = ['', 'ds', 'co', 'os', 'cn']
const subjectLabels: Record<string, string> = { '': '全部科目', ds: '数据结构', co: '计组', os: '操作系统', cn: '网络' }
const typeOptions = ['', 'fill_gap', 'debug', 'trace', 'design']
const typeLabels: Record<string, string> = { '': '全部类型', fill_gap: '补全', debug: '调试', trace: '追踪', design: '设计' }
const difficultyOptions = ['', 'easy', 'medium', 'hard']
const diffLabels: Record<string, string> = { '': '全部难度', easy: '简单', medium: '中等', hard: '困难' }

type BadgeVariant = 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'amber'

function getDifficultyBadge(d: string): BadgeVariant {
  const m: Record<string, BadgeVariant> = { easy: 'success', medium: 'warning', hard: 'danger' }
  return m[d] || 'info'
}
function getTypeLabel(t: string) { return typeLabels[t] || t }

async function loadChallenges() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    const res = await getChallenges(filters.value)
    challenges.value = res.challenges || []
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '加载挑战列表失败'
  } finally { isLoading.value = false }
}

async function openChallenge(id: string) {
  isLoading.value = true
  try {
    const challenge = await getChallenge(id)
    currentChallenge.value = challenge
    userCode.value = challenge.starter_code || ''
    executionResult.value = null
    explanation.value = ''
    showExplanation.value = false
    activeTab.value = 'code'
    stage.value = 'detail'
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '加载挑战失败'
  } finally { isLoading.value = false }
}

async function handleExecute() {
  if (!userCode.value.trim()) return
  submitting.value = true
  try {
    executionResult.value = await executeCode({
      code: userCode.value,
      challenge_id: currentChallenge.value?.id || '',
    })
    activeTab.value = 'result'
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '执行失败'
  } finally { submitting.value = false }
}

async function handleSubmit() {
  if (!currentChallenge.value) return
  submitting.value = true
  try {
    executionResult.value = await submitAnswer(currentChallenge.value.id, {
      code: userCode.value,
      challenge_id: currentChallenge.value.id,
    })
    stage.value = 'result'
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.detail || '提交失败'
  } finally { submitting.value = false }
}

async function handleRevealExplanation() {
  if (!currentChallenge.value) return
  try {
    const res = await getExplanation(currentChallenge.value.id)
    explanation.value = res.explanation || ''
    showExplanation.value = true
  } catch { /* ignore */ }
}

function backToList() {
  stage.value = 'list'
  currentChallenge.value = null
  executionResult.value = null
  loadChallenges()
}

const passedCount = computed(() => challenges.value.filter(c => c.status === 'completed').length)

loadChallenges()
</script>

<template>
  <div class="code-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon"><Code2 :size="22" class="text-white" /></div>
        <div>
          <h1 class="header-title">代码实战</h1>
          <p class="header-sub">算法可视化调试 · 补全/追踪/设计/调试 四种挑战</p>
        </div>
      </div>
      <Button v-if="stage !== 'list'" variant="ghost" size="sm" @click="backToList">
        <ArrowLeft :size="16" /> 返回列表
      </Button>
    </div>

    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>

    <!-- Stage: List -->
    <div v-if="stage === 'list'" class="list-stage">
      <!-- Filters -->
      <div class="filter-bar">
        <select v-model="filters.subject" @change="loadChallenges" class="filter-select">
          <option v-for="s in subjectOptions" :key="s" :value="s">{{ subjectLabels[s] }}</option>
        </select>
        <select v-model="filters.type" @change="loadChallenges" class="filter-select">
          <option v-for="t in typeOptions" :key="t" :value="t">{{ typeLabels[t] }}</option>
        </select>
        <select v-model="filters.difficulty" @change="loadChallenges" class="filter-select">
          <option v-for="d in difficultyOptions" :key="d" :value="d">{{ diffLabels[d] }}</option>
        </select>
        <span class="filter-stats">{{ passedCount }} / {{ challenges.length }} 已完成</span>
      </div>

      <div v-if="isLoading" class="loading-stage"><Loader2 :size="36" class="spinning text-primary" /></div>

      <div v-else class="challenge-grid">
        <Card
          v-for="ch in challenges" :key="ch.id"
          padding="lg" hoverable
          :class="['challenge-card', { completed: ch.status === 'completed' }]"
          @click="openChallenge(ch.id)"
        >
          <div class="ch-top">
            <div class="ch-icon" :class="ch.type">
              <component :is="ch.type === 'fill_gap' ? Triangle : ch.type === 'debug' ? Zap : ch.type === 'trace' ? TrendingUp : Lightbulb" :size="20" />
            </div>
            <div class="ch-info">
              <h3>{{ ch.title }}</h3>
              <p>{{ ch.description?.slice(0, 60) }}...</p>
            </div>
          </div>
          <div class="ch-meta">
            <Badge :variant="getDifficultyBadge(ch.difficulty)" size="sm">{{ diffLabels[ch.difficulty] || ch.difficulty }}</Badge>
            <Badge variant="info" size="sm">{{ getTypeLabel(ch.type) }}</Badge>
            <span v-if="ch.topic" class="ch-topic">{{ ch.topic }}</span>
            <CheckCircle2 v-if="ch.status === 'completed'" :size="18" class="text-success" />
          </div>
        </Card>
      </div>
    </div>

    <!-- Stage: Detail -->
    <div v-if="stage === 'detail' && currentChallenge" class="detail-stage">
      <div class="detail-layout">
        <!-- Left: Description -->
        <div class="detail-left">
          <Card padding="lg">
            <div class="detail-header">
              <h2>{{ currentChallenge.title }}</h2>
              <div class="detail-badges">
                <Badge :variant="getDifficultyBadge(currentChallenge.difficulty)" size="sm">{{ diffLabels[currentChallenge.difficulty] || currentChallenge.difficulty }}</Badge>
                <Badge variant="info" size="sm">{{ getTypeLabel(currentChallenge.type) }}</Badge>
              </div>
            </div>
            <p class="detail-desc">{{ currentChallenge.description }}</p>
            <div v-if="currentChallenge.constraints?.length" class="constraints">
              <h4>约束条件</h4>
              <ul><li v-for="c in currentChallenge.constraints" :key="c">{{ c }}</li></ul>
            </div>
            <div v-if="currentChallenge.examples?.length" class="examples">
              <h4>示例</h4>
              <div v-for="(ex, i) in currentChallenge.examples" :key="i" class="example-item">
                <span class="ex-label">输入:</span><code>{{ ex.input }}</code>
                <span class="ex-label">输出:</span><code>{{ ex.output }}</code>
              </div>
            </div>
          </Card>
        </div>

        <!-- Right: Code Editor -->
        <div class="detail-right">
          <div class="tab-bar">
            <button :class="['tab', { active: activeTab === 'code' }]" @click="activeTab = 'code'">代码</button>
            <button :class="['tab', { active: activeTab === 'result' }]" @click="activeTab = 'result'" :disabled="!executionResult">结果</button>
          </div>

          <div v-if="activeTab === 'code'" class="code-panel">
            <textarea
              v-model="userCode"
              class="code-editor"
              spellcheck="false"
              placeholder="# 在这里编写你的代码..."
            ></textarea>
            <div class="code-actions">
              <Button variant="primary" size="sm" :loading="submitting" @click="handleExecute">
                <Play :size="16" /> 运行
              </Button>
              <Button variant="outline" size="sm" :disabled="submitting" @click="handleSubmit">
                <Send :size="16" /> 提交
              </Button>
            </div>
          </div>

          <div v-if="activeTab === 'result' && executionResult" class="result-panel">
            <div :class="['result-header', executionResult.passed ? 'passed' : 'failed']">
              <CheckCircle2 v-if="executionResult.passed" :size="20" />
              <XCircle v-else :size="20" />
              <span>{{ executionResult.passed ? '通过' : '未通过' }}</span>
            </div>
            <pre class="result-output">{{ executionResult.output || executionResult.error || '(无输出)' }}</pre>
            <div v-if="executionResult.steps?.length" class="steps-preview">
              <div v-for="s in executionResult.steps" :key="s.step_no" class="step-row">
                <span class="step-no">{{ s.step_no }}</span>
                <span class="step-desc">{{ s.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Explanation -->
      <div v-if="showExplanation && explanation" class="explanation-section">
        <Card padding="lg">
          <h3><BookOpen :size="18" /> 解析</h3>
          <p>{{ explanation }}</p>
        </Card>
      </div>
      <div v-if="!showExplanation && executionResult" class="reveal-row">
        <Button variant="outline" size="sm" @click="handleRevealExplanation">
          <Lightbulb :size="16" /> 查看解析
        </Button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.code-page { max-width: 960px; margin: 0 auto; padding: 1.5rem; }

.page-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 1.5rem; }
.header-left { display: flex; align-items: center; gap: 0.8rem; }
.header-icon {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #ef4444, #f97316);
  border-radius: 14px; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(239,68,68,0.3);
}
.header-title { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary); }
.header-sub { font-size: 0.85rem; color: var(--color-text-secondary); margin-top: 0.15rem; }

.error-toast { background: #fef2f2; color: #dc2626; padding: 0.7rem 1rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.85rem; border: 1px solid #fecaca; }

.loading-stage { text-align: center; padding: 3rem 0; }
.spinning { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.text-primary { color: var(--color-primary-500); }
.text-success { color: var(--color-success-500); }

/* Filters */
.filter-bar { display: flex; gap: 0.5rem; margin-bottom: 1.2rem; align-items: center; flex-wrap: wrap; }
.filter-select {
  padding: 0.45rem 0.7rem; border: 1.5px solid var(--color-border); border-radius: 8px;
  font-size: 0.85rem; background: var(--color-bg-primary); color: var(--color-text-primary);
  outline: none; cursor: pointer;
}
.filter-select:focus { border-color: var(--color-primary-400); }
.filter-stats { margin-left: auto; font-size: 0.82rem; color: var(--color-text-muted); }

/* Challenge Grid */
.challenge-grid { display: flex; flex-direction: column; gap: 0.6rem; }
.challenge-card { cursor: pointer; transition: all 0.2s; }
.challenge-card.completed { opacity: 0.65; }
.ch-top { display: flex; gap: 0.8rem; align-items: flex-start; }
.ch-icon {
  width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center;
  justify-content: center; flex-shrink: 0; color: white;
}
.ch-icon.fill_gap { background: linear-gradient(135deg, #f59e0b, #fbbf24); }
.ch-icon.debug { background: linear-gradient(135deg, #ef4444, #f87171); }
.ch-icon.trace { background: linear-gradient(135deg, #6366f1, #818cf8); }
.ch-icon.design { background: linear-gradient(135deg, #10b981, #34d399); }
.ch-info h3 { font-size: 0.95rem; font-weight: 600; color: var(--color-text-primary); }
.ch-info p { font-size: 0.8rem; color: var(--color-text-secondary); margin-top: 0.15rem; }
.ch-meta { display: flex; gap: 0.4rem; align-items: center; margin-top: 0.6rem; }
.ch-topic { font-size: 0.78rem; color: var(--color-text-muted); }

/* Detail Layout */
.detail-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.8rem; }
.detail-header h2 { font-size: 1.15rem; font-weight: 700; color: var(--color-text-primary); }
.detail-badges { display: flex; gap: 0.3rem; }
.detail-desc { font-size: 0.9rem; color: var(--color-text-secondary); line-height: 1.7; }
.constraints, .examples { margin-top: 1rem; }
.constraints h4, .examples h4 { font-size: 0.85rem; font-weight: 600; color: var(--color-text-primary); margin-bottom: 0.4rem; }
.constraints li { font-size: 0.82rem; color: var(--color-text-secondary); margin-left: 1rem; }
.example-item { margin-bottom: 0.5rem; }
.ex-label { font-size: 0.78rem; color: var(--color-text-muted); margin-right: 0.3rem; }
.example-item code { font-size: 0.82rem; background: var(--color-bg-secondary); padding: 0.15rem 0.4rem; border-radius: 4px; }

/* Code Panel */
.detail-right { display: flex; flex-direction: column; }
.tab-bar { display: flex; gap: 0; margin-bottom: 0; }
.tab {
  padding: 0.45rem 1rem; border: 1.5px solid var(--color-border); border-bottom: none;
  background: var(--color-bg-secondary); color: var(--color-text-muted);
  font-size: 0.85rem; cursor: pointer; border-radius: 8px 8px 0 0; transition: all 0.2s;
}
.tab.active { background: var(--color-bg-primary); color: var(--color-text-primary); font-weight: 600; }
.tab:disabled { opacity: 0.4; cursor: not-allowed; }
.code-panel {
  flex: 1; border: 1.5px solid var(--color-border); border-radius: 0 8px 8px 8px;
  display: flex; flex-direction: column; overflow: hidden;
}
.code-editor {
  flex: 1; min-height: 280px; padding: 1rem; border: none; outline: none; resize: vertical;
  font-family: 'Fira Code', 'Cascadia Code', 'JetBrains Mono', monospace;
  font-size: 0.85rem; line-height: 1.6; background: #1e1e2e; color: #cdd6f4;
  tab-size: 4;
}
.code-actions { display: flex; gap: 0.5rem; padding: 0.6rem; border-top: 1px solid var(--color-border); background: var(--color-bg-secondary); }

/* Result Panel */
.result-panel {
  flex: 1; border: 1.5px solid var(--color-border); border-radius: 0 8px 8px 8px;
  padding: 1rem; overflow-y: auto; background: var(--color-bg-primary);
}
.result-header { display: flex; align-items: center; gap: 0.4rem; padding: 0.5rem 0.8rem; border-radius: 8px; font-weight: 600; font-size: 0.9rem; margin-bottom: 0.8rem; }
.result-header.passed { background: rgba(16,185,129,0.1); color: var(--color-success-500); }
.result-header.failed { background: rgba(239,68,68,0.1); color: #ef4444; }
.result-output {
  font-family: 'Fira Code', 'Cascadia Code', monospace; font-size: 0.82rem;
  background: #1e1e2e; color: #cdd6f4; padding: 0.8rem; border-radius: 8px;
  white-space: pre-wrap; max-height: 200px; overflow-y: auto;
}
.steps-preview { margin-top: 0.8rem; display: flex; flex-direction: column; gap: 0.3rem; }
.step-row { display: flex; gap: 0.5rem; font-size: 0.82rem; padding: 0.25rem 0; }
.step-no {
  width: 24px; height: 24px; border-radius: 50%; background: var(--color-primary-100);
  color: var(--color-primary-600); display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700; flex-shrink: 0;
}
.step-desc { color: var(--color-text-secondary); line-height: 1.5; }

.explanation-section { margin-bottom: 0.8rem; }
.explanation-section h3 { display: flex; align-items: center; gap: 0.4rem; font-size: 0.95rem; font-weight: 600; color: var(--color-text-primary); margin-bottom: 0.5rem; }
.explanation-section p { font-size: 0.88rem; color: var(--color-text-secondary); line-height: 1.7; }
.reveal-row { text-align: center; }

@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; }
  .code-page { padding: 1rem; }
  .filter-bar { flex-direction: column; }
  .filter-stats { margin-left: 0; }
}
</style>
