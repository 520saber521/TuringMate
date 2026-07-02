<script setup lang="ts">
import { ref, computed } from 'vue'
import { Brain, ChevronDown, ChevronUp, Sparkles, Lightbulb } from 'lucide-vue-next'
import type { StepItem } from '@/api/questionBank'

const props = defineProps<{
  solutionSteps: StepItem[]
  aiAnalysis?: string | null
  questionContent: string
}>()

const expanded = ref(false)
const expandedSteps = ref<Set<number>>(new Set())
const loading = ref(false)
const generatedAnalysis = ref<string | null>(null)

function togglePanel() {
  expanded.value = !expanded.value
}

function toggleStep(stepNo: number) {
  if (expandedSteps.value.has(stepNo)) {
    expandedSteps.value.delete(stepNo)
  } else {
    expandedSteps.value.add(stepNo)
  }
}

function isExpanded(stepNo: number) {
  return expandedSteps.value.has(stepNo)
}

async function generateAnalysis() {
  if (loading.value || generatedAnalysis.value) return
  loading.value = true
  // Simulate AI analysis generation (in production, call API)
  await new Promise(r => setTimeout(r, 2000))
  generatedAnalysis.value = `这道题考察的是${props.questionContent.slice(0, 30)}...相关的核心概念。\n\n**解题关键点：**\n1. 理解题目的数据结构特点和约束条件\n2. 选择最优的算法策略（时间和空间复杂度权衡）\n3. 注意边界条件和特殊情况处理\n\n**类似题型：**\n- 历年408真题中类似题目反复出现\n- 建议结合教材对应章节的习题进行巩固`
  loading.value = false
}

const hasAnalysis = computed(() => props.aiAnalysis || generatedAnalysis.value)
</script>

<template>
  <div class="ai-panel" :class="{ expanded }">
    <!-- Toggle Button -->
    <button class="ai-panel__toggle" @click="togglePanel">
      <div class="ai-panel__toggle-left">
        <Brain :size="20" class="ai-panel__icon" />
        <span class="ai-panel__title">AI 智能解析</span>
        <span class="ai-panel__badge">苏格拉底式</span>
      </div>
      <component :is="expanded ? ChevronUp : ChevronDown" :size="18" />
    </button>

    <!-- Panel Content -->
    <div class="ai-panel__body" v-if="expanded">
      <!-- Step-by-step solution -->
      <div class="ai-panel__steps">
        <h4 class="ai-panel__section-title">
          <Lightbulb :size="15" /> 逐步引导
        </h4>
        <div
          v-for="step in solutionSteps"
          :key="step.step_no"
          class="ai-step"
          :class="{ open: isExpanded(step.step_no) }"
        >
          <button class="ai-step__header" @click="toggleStep(step.step_no)">
            <span class="ai-step__num">步骤 {{ step.step_no }}</span>
            <span class="ai-step__preview">{{ step.content.slice(0, 40) }}...</span>
            <component :is="isExpanded(step.step_no) ? ChevronUp : ChevronDown" :size="14" class="ai-step__chevron" />
          </button>
          <div class="ai-step__detail" v-if="isExpanded(step.step_no)">
            <p>{{ step.content }}</p>
            <div class="ai-step__hint" v-if="step.hint">
              <span class="hint-label">💡 提示：</span> {{ step.hint }}
            </div>
          </div>
        </div>
      </div>

      <!-- AI Analysis -->
      <div class="ai-panel__analysis" v-if="hasAnalysis">
        <h4 class="ai-panel__section-title">
          <Sparkles :size="15" /> 深度分析
        </h4>
        <div class="ai-analysis__content" v-text="hasAnalysis"></div>
      </div>

      <!-- Generate Button -->
      <div class="ai-panel__generate" v-if="!hasAnalysis && !loading">
        <p class="generate-hint">点击生成苏格拉底式解题分析</p>
        <button class="generate-btn" @click="generateAnalysis">
          <Sparkles :size="15" /> 生成 AI 解析
        </button>
      </div>
      <div class="ai-panel__loading" v-if="loading">
        <div class="loading-dots">
          <span></span><span></span><span></span>
        </div>
        <p>正在生成 AI 解析...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ai-panel {
  border-radius: 16px;
  border: 1px solid rgba(139,92,246,0.15);
  background: white;
  overflow: hidden;
  transition: box-shadow 0.2s;
}
.ai-panel.expanded {
  box-shadow: 0 4px 24px rgba(139,92,246,0.08);
}

.ai-panel__toggle {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%; padding: 1rem 1.25rem;
  border: none; background: none; cursor: pointer;
  font-family: inherit; color: #1f2937;
  transition: background 0.15s;
}
.ai-panel__toggle:hover { background: rgba(139,92,246,0.03); }
.ai-panel__toggle-left { display: flex; align-items: center; gap: 0.5rem; }
.ai-panel__icon { color: #7c3aed; }
.ai-panel__title { font-weight: 700; font-size: 0.95rem; }
.ai-panel__badge {
  font-size: 0.7rem; padding: 0.15rem 0.5rem;
  border-radius: 999px; background: rgba(139,92,246,0.1); color: #8b5cf6;
  font-weight: 600;
}

.ai-panel__body {
  padding: 0 1.25rem 1.25rem;
  display: flex; flex-direction: column; gap: 1rem;
}

.ai-panel__section-title {
  display: flex; align-items: center; gap: 0.4rem;
  font-size: 0.85rem; font-weight: 600; color: #374151; margin: 0 0 0.5rem;
}

.ai-step {
  border-radius: 10px; border: 1px solid rgba(0,0,0,0.06);
  margin-bottom: 0.5rem; overflow: hidden;
  transition: all 0.15s;
}
.ai-step.open { border-color: rgba(139,92,246,0.2); background: rgba(139,92,246,0.02); }
.ai-step__header {
  display: flex; align-items: center; gap: 0.5rem;
  width: 100%; padding: 0.65rem 0.85rem;
  border: none; background: none; cursor: pointer;
  font-family: inherit; text-align: left;
  transition: background 0.15s;
}
.ai-step__header:hover { background: rgba(0,0,0,0.02); }
.ai-step__num {
  font-size: 0.72rem; font-weight: 700; padding: 0.15rem 0.45rem;
  border-radius: 6px; background: rgba(139,92,246,0.1); color: #7c3aed;
  flex-shrink: 0;
}
.ai-step__preview {
  flex: 1; font-size: 0.82rem; color: #6b7280;
}
.ai-step__chevron { color: #cbd5e1; flex-shrink: 0; }
.ai-step__detail {
  padding: 0.5rem 0.85rem 0.85rem;
  font-size: 0.85rem; color: #374151; line-height: 1.65;
}
.ai-step__hint {
  margin-top: 0.5rem; padding: 0.5rem 0.75rem;
  border-radius: 8px; background: #fffbeb; color: #92400e;
  font-size: 0.8rem;
}

.ai-analysis__content {
  font-size: 0.85rem; color: #374151; line-height: 1.7;
  white-space: pre-wrap;
}

.ai-panel__generate { text-align: center; padding: 0.5rem; }
.generate-hint { font-size: 0.8rem; color: #9ca3af; margin-bottom: 0.5rem; }
.generate-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.55rem 1.25rem; border-radius: 12px;
  border: none; background: linear-gradient(135deg, #7c3aed, #8b5cf6);
  color: white; font-size: 0.85rem; font-weight: 600; cursor: pointer; font-family: inherit;
  transition: all 0.2s;
}
.generate-btn:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(124,58,237,0.3); }

.ai-panel__loading { text-align: center; padding: 0.5rem; color: #9ca3af; font-size: 0.85rem; }

.loading-dots {
  display: flex; justify-content: center; gap: 0.3rem; margin-bottom: 0.5rem;
}
.loading-dots span {
  width: 6px; height: 6px; border-radius: 50%; background: #8b5cf6;
  animation: dotBounce 1.2s infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotBounce {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}
</style>
