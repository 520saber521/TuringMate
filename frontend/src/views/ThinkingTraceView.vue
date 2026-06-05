<script setup lang="ts">
import { ref, computed } from 'vue'
import { Brain, TrendingUp, Target, AlertTriangle, Zap, ChevronRight, Loader2, ArrowRight, Lightbulb, GitBranch } from 'lucide-vue-next'
import Card from '@/components/ui/Card.vue'
import Badge from '@/components/ui/Badge.vue'
import Button from '@/components/ui/Button.vue'
import { getThinkingPath, getWeeklyReport } from '@/api/thinking'
import type { ThinkingPath, WeeklyReport, TraceStep } from '@/api/thinking'

const isLoading = ref(false)
const errorMsg = ref('')
const activeTab = ref<'path' | 'report'>('path')

// Path
const sessionId = ref('')
const pathData = ref<ThinkingPath | null>(null)
const selectedStep = ref<TraceStep | null>(null)

// Report
const reportData = ref<WeeklyReport | null>(null)

const stepTypeConfig: Record<string, { icon: any; color: string; label: string }> = {
  correct: { icon: Target, color: 'var(--color-success-500)', label: '正确推理' },
  jump: { icon: ChevronRight, color: 'var(--color-warning-500)', label: '思维跳跃' },
  deviation: { icon: GitBranch, color: 'var(--color-danger-500)', label: '偏离' },
  stuck: { icon: AlertTriangle, color: 'var(--color-accent-500, #f472b6)', label: '卡点' },
}

async function loadPath() {
  if (!sessionId.value.trim()) {
    errorMsg.value = '请输入会话ID'
    return
  }
  isLoading.value = true
  errorMsg.value = ''
  try {
    pathData.value = await getThinkingPath(sessionId.value)
  } catch (e: any) {
    errorMsg.value = '加载思维路径失败'
  } finally {
    isLoading.value = false
  }
}

async function loadReport() {
  isLoading.value = true
  errorMsg.value = ''
  try {
    reportData.value = await getWeeklyReport('current')
  } catch (e: any) {
    errorMsg.value = '加载成长报告失败'
  } finally {
    isLoading.value = false
  }
}

function selectStep(step: TraceStep) {
  selectedStep.value = selectedStep.value?.step_number === step.step_number ? null : step
}
</script>

<template>
  <div class="thinking-page">
    <div class="tt-intro">
      <p class="tt-intro__overline font-serif">思维实验室</p>
      <h1 class="tt-intro__title">看见你的思考过程</h1>
      <p class="tt-intro__desc">不止看结果，回放整个推理路径 — 在哪儿卡住了？走了哪条弯路？</p>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button :class="['tab', { active: activeTab === 'path' }]" @click="activeTab = 'path'">
        <GitBranch :size="16" />
        思维路径
      </button>
      <button :class="['tab', { active: activeTab === 'report' }]" @click="activeTab = 'report'; loadReport()">
        <TrendingUp :size="16" />
        成长报告
      </button>
    </div>

    <div v-if="errorMsg" class="error-toast">{{ errorMsg }}</div>

    <!-- Path Tab -->
    <div v-if="activeTab === 'path'" class="path-tab">
      <div class="session-input-row">
        <input
          v-model="sessionId"
          class="session-input"
          placeholder="输入会话ID查看思维路径..."
          aria-label="会话ID"
          @keyup.enter="loadPath"
        />
        <Button variant="primary" :loading="isLoading" @click="loadPath">
          <ArrowRight :size="16" />
          查看
        </Button>
      </div>

      <div v-if="!pathData && !isLoading" class="empty-hint">
        <Brain :size="48" class="empty-hint__icon" />
        <p>输入一个苏格拉底对话的会话ID，查看AI分析出的思维链路</p>
      </div>

      <!-- Path visualization -->
      <div v-if="pathData" class="path-visual">
        <!-- Conclusion -->
        <div class="conclusion-card" :class="pathData.final_state === 'mastered' ? 'surface-glow' : 'surface-paper'">
          <div class="conclusion-inner">
            <div class="conclusion-header">
              <Lightbulb :size="20" class="conclusion-icon" />
              <span>AI 结论: {{ pathData.conclusion }}</span>
            </div>
            <Badge :variant="pathData.final_state === 'mastered' ? 'success' : pathData.final_state === 'stuck' ? 'danger' : 'warning'">
              {{ pathData.final_state === 'mastered' ? '已掌握' : pathData.final_state === 'stuck' ? '卡住' : '进行中' }}
            </Badge>
          </div>
        </div>

        <!-- Steps timeline -->
        <div class="steps-timeline">
          <div
            v-for="step in pathData.steps" :key="step.step_number"
            :class="['step-node', { selected: selectedStep?.step_number === step.step_number }]"
            @click="selectStep(step)"
          >
            <div class="step-line">
              <div class="step-dot" :style="{ background: stepTypeConfig[step.step_type]?.color }">
                <component :is="stepTypeConfig[step.step_type]?.icon" :size="12" class="text-white" />
              </div>
              <div class="step-connector" v-if="step.step_number < pathData.steps.length"></div>
            </div>
            <div class="step-body">
              <div class="step-header">
                <span class="step-num">Step {{ step.step_number }}</span>
                <Badge size="sm" :variant="step.step_type === 'correct' ? 'success' : step.step_type === 'stuck' ? 'danger' : 'warning'">
                  {{ stepTypeConfig[step.step_type]?.label }}
                </Badge>
                <span class="step-confidence">{{ Math.round(step.confidence * 100) }}% 置信</span>
              </div>
              <p class="step-title">{{ step.title }}</p>
              <div v-if="selectedStep?.step_number === step.step_number" class="step-detail">
                <p>{{ step.content }}</p>
                <div v-if="step.gap_labels.length" class="gap-tags">
                  <span v-for="g in step.gap_labels" :key="g" class="gap-tag">{{ g }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Tab -->
    <div v-if="activeTab === 'report'" class="report-tab">
      <div v-if="!reportData && !isLoading" class="report-empty">
        <div class="report-empty__inner">
          <TrendingUp :size="48" class="report-empty__icon" />
          <p class="font-serif">查看你的思维成长轨迹</p>
          <Button variant="primary" :loading="isLoading" @click="loadReport">
            生成成长报告
          </Button>
        </div>
      </div>

      <div v-if="reportData" class="report-content">
        <!-- Radar scores -->
        <div class="report-card surface-paper">
          <h3 class="report-card__title">能力维度</h3>
          <div class="radar-scores">
            <div class="score-item">
              <span class="score-label">逻辑性</span>
              <div class="score-bar-track">
                <div class="score-bar-fill score-bar-fill--logic" :style="{ width: `${reportData.radar_scores.logic}%` }"></div>
              </div>
              <span class="score-val">{{ reportData.radar_scores.logic }}</span>
            </div>
            <div class="score-item">
              <span class="score-label">完整性</span>
              <div class="score-bar-track">
                <div class="score-bar-fill score-bar-fill--complete" :style="{ width: `${reportData.radar_scores.completeness}%` }"></div>
              </div>
              <span class="score-val">{{ reportData.radar_scores.completeness }}</span>
            </div>
            <div class="score-item">
              <span class="score-label">速度</span>
              <div class="score-bar-track">
                <div class="score-bar-fill score-bar-fill--speed" :style="{ width: `${reportData.radar_scores.speed}%` }"></div>
              </div>
              <span class="score-val">{{ reportData.radar_scores.speed }}</span>
            </div>
          </div>
        </div>

        <!-- Gap stats -->
        <div v-if="reportData.gap_stats && Object.keys(reportData.gap_stats).length" class="report-card surface-paper">
          <h3 class="report-card__title">漏洞分布</h3>
          <div class="gap-chips">
            <span v-for="(count, label) in reportData.gap_stats" :key="label" class="gap-chip">
              {{ label }} <strong>{{ count }}次</strong>
            </span>
          </div>
        </div>

        <!-- Top concerns -->
        <div v-if="reportData.top_concerns.length" class="report-card surface-paper">
          <h3 class="report-card__title">重点关注</h3>
          <ul class="concerns-list">
            <li v-for="c in reportData.top_concerns" :key="c">
              <AlertTriangle :size="14" class="concern-icon" />
              {{ c }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.thinking-page { max-width: 800px; margin: 0 auto; padding: 1.5rem; }

/* ============================
   INTRO — Lab feel
   ============================ */
.tt-intro {
  text-align: center;
  margin-bottom: 1.5rem;
}
.tt-intro__overline {
  font-size: 0.88rem;
  color: var(--color-amber-600);
  letter-spacing: 0.04em;
  margin-bottom: 0.4rem;
}
.tt-intro__title {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: -0.01em;
  margin-bottom: 0.3rem;
}
.tt-intro__desc {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

/* ============================
   TABS
   ============================ */
.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 1.5rem;
  background: var(--color-bg-secondary);
  padding: 4px;
  border-radius: var(--radius-lg);
}
.tab {
  flex: 1;
  padding: 0.55rem 0.8rem;
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  font-weight: 500;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  font-family: inherit;
}
.tab:hover {
  color: var(--color-text-primary);
}
.tab.active {
  background: var(--surface-paper-bg);
  color: var(--color-primary-600);
  box-shadow: var(--shadow-sm);
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
   PATH TAB
   ============================ */
.session-input-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.session-input {
  flex: 1;
  padding: 0.65rem 0.85rem;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.88rem;
  outline: none;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  box-sizing: border-box;
  font-family: inherit;
  transition: border-color var(--transition-fast);
}
.session-input:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px var(--color-border-focus);
}

.empty-hint {
  text-align: center;
  padding: 3rem 0;
  color: var(--color-text-muted);
}
.empty-hint__icon {
  margin-bottom: 1rem;
  opacity: 0.25;
}

/* Conclusion */
.conclusion-card {
  margin-bottom: 1.5rem;
}
.conclusion-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
}
.conclusion-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
.conclusion-icon {
  color: var(--color-amber-500);
  flex-shrink: 0;
}

/* Steps Timeline */
.steps-timeline {
  display: flex;
  flex-direction: column;
}
.step-node {
  display: flex;
  gap: 0.8rem;
  cursor: pointer;
  padding: 0.25rem 0;
  transition: background var(--transition-fast);
}
.step-node:hover {
  background: rgba(124, 58, 237, 0.02);
  border-radius: var(--radius-sm);
}
.step-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 28px;
  flex-shrink: 0;
}
.step-dot {
  width: 28px; height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  transition: transform var(--transition-fast);
}
.step-node.selected .step-dot {
  transform: scale(1.15);
}
.step-connector {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: var(--color-border);
  margin: 4px 0;
}
.step-body {
  flex: 1;
  padding-bottom: 0.8rem;
  min-width: 0;
}
.step-header {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-bottom: 0.2rem;
  flex-wrap: wrap;
}
.step-num {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
}
.step-confidence {
  font-size: 0.72rem;
  color: var(--color-text-muted);
  margin-left: auto;
}
.step-title {
  font-size: 0.9rem;
  color: var(--color-text-primary);
  font-weight: 500;
  line-height: 1.5;
}
.step-detail {
  margin-top: 0.5rem;
  padding: 0.75rem 0.85rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  border: 1px solid var(--color-border-light);
}
.gap-tags {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}
.gap-tag {
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-size: 0.72rem;
  background: var(--color-bg-danger-soft);
  color: var(--color-danger-600);
  border: 1px solid var(--color-danger-200);
}

/* ============================
   REPORT TAB
   ============================ */
.report-tab { padding: 0.5rem 0; }
.report-empty {
  text-align: center;
  padding: 3rem 0;
}
.report-empty__inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.8rem;
}
.report-empty__icon {
  color: var(--color-text-muted);
  opacity: 0.3;
}
.report-empty__inner p {
  font-size: 1rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.report-card {
  padding: 1.25rem;
}
.report-card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 1rem;
}

/* Radar scores */
.radar-scores {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}
.score-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.score-label {
  width: 56px;
  font-size: 0.82rem;
  color: var(--color-text-secondary);
  flex-shrink: 0;
  font-weight: 500;
}
.score-bar-track {
  flex: 1;
  height: 8px;
  background: var(--color-border-light);
  border-radius: 4px;
  overflow: hidden;
}
.score-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.score-bar-fill--logic {
  background: linear-gradient(90deg, var(--color-primary-400), var(--color-primary-600));
}
.score-bar-fill--complete {
  background: linear-gradient(90deg, var(--color-success-400), var(--color-success-600));
}
.score-bar-fill--speed {
  background: linear-gradient(90deg, var(--color-amber-400), var(--color-amber-600));
}
.score-val {
  width: 30px;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text-primary);
  text-align: right;
}

/* Gap chips */
.gap-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.gap-chip {
  padding: 0.3rem 0.7rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-100);
  color: var(--color-text-secondary);
}
.gap-chip strong {
  color: var(--color-primary-600);
}

/* Concerns */
.concerns-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.concerns-list li {
  display: flex;
  align-items: flex-start;
  gap: 0.45rem;
  font-size: 0.88rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
.concern-icon {
  color: var(--color-amber-500);
  flex-shrink: 0;
  margin-top: 0.15rem;
}

@media (max-width: 640px) {
  .thinking-page { padding: 1rem; }
  .tt-intro__title { font-size: 1.3rem; }
}
</style>
