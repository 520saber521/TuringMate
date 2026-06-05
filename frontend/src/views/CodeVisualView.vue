<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, Play, Pause, SkipForward, SkipBack, RotateCcw, Code2, ChevronDown, Zap } from 'lucide-vue-next'
import { useAlgorithmPlayer } from '@/composables/useAlgorithmPlayer'
import { algorithmRegistry, getAlgorithmsByCategory, categoryLabels, type AlgorithmDef, type AlgoCategory, type ArrayElement, type ListNode, type TreeNode, type AlgorithmStep } from '@/data/algorithms'
import { codeMap } from '@/data/algorithmCode'
import { getQuestionsForAlgo } from '@/data/examQuestions'
import apiClient from '@/api/index'

const router = useRouter()
const {
  steps,
  currentIndex,
  currentStep: currentStepRef,
  totalSteps,
  isPlaying,
  isComplete: playerIsComplete,
  isRunning,
  error,
  speed,
  speedOptions,
  progress,
  selectedAlgorithm,
  runAlgorithm: execAlgorithm,
  play,
  pause,
  togglePlay,
  stepForward,
  stepBack,
  reset,
  setSpeed,
} = useAlgorithmPlayer()

const showAlgoMenu = ref(false)
const selectedId = ref(algorithmRegistry[0]?.id || '')
const inputRaw = ref('')
const extraParam = ref('')
const codeLang = ref<'pseudo' | 'c' | 'python'>('pseudo')
const compareMode = ref(false)
const compareId = ref('')
const compareSteps = ref(0)
const compareResult = ref('')
const aiExplanation = ref('')
const aiLoading = ref(false)
const showTreeBuilder = ref(false)

// ── Derived ──

const selectedAlgo = computed(() => algorithmRegistry.find(a => a.id === selectedId.value) || null)

const algorithmsByCategory = computed(() => {
  const map = getAlgorithmsByCategory()
  return Object.entries(map).map(([cat, algos]) => ({
    category: cat as AlgoCategory,
    label: categoryLabels[cat as AlgoCategory],
    algos,
  }))
})

const currentStep = computed(() => currentStepRef.value)
const isPseudoLine = (lineIdx: number) => currentStep.value?.lineNumber === lineIdx + 1

const needsExtraParam = computed(() => {
  const id = selectedId.value
  return id === 'binary-search' || id === 'linked-list-delete'
})

const extraParamLabel = computed(() => {
  if (selectedId.value === 'binary-search') return '查找目标'
  if (selectedId.value === 'linked-list-delete') return '要删除的值'
  return ''
})

const treePresets = [
  {
    label: '完全二叉树',
    json: { value: 1, left: { value: 2, left: { value: 4, left: null, right: null }, right: { value: 5, left: null, right: null } }, right: { value: 3, left: { value: 6, left: null, right: null }, right: { value: 7, left: null, right: null } } },
  },
  {
    label: 'BST',
    json: { value: 5, left: { value: 3, left: { value: 2, left: null, right: null }, right: { value: 4, left: null, right: null } }, right: { value: 8, left: { value: 6, left: null, right: null }, right: { value: 9, left: null, right: null } } },
  },
  {
    label: '右斜树',
    json: { value: 1, left: null, right: { value: 2, left: null, right: { value: 3, left: null, right: { value: 4, left: null, right: null } } } },
  },
]

function selectAlgorithm(id: string) {
  selectedId.value = id
  showAlgoMenu.value = false
  const algo = algorithmRegistry.find(a => a.id === id)
  if (!algo) return

  selectedAlgorithm.value = algo
  inputRaw.value = algo.defaultInput

  // Set extra params for special algorithms
  if (id === 'binary-search') {
    const parsed = JSON.parse(algo.defaultInput)
    inputRaw.value = parsed.arr.join(',')
    extraParam.value = String(parsed.target)
  } else if (id === 'linked-list-delete') {
    const parsed = JSON.parse(algo.defaultInput)
    inputRaw.value = parsed.values.join(',')
    extraParam.value = String(parsed.x)
  } else if (algo.category === 'sorting' || algo.category === 'heap') {
    const parsed = JSON.parse(algo.defaultInput)
    inputRaw.value = parsed.arr.join(',')
  } else if (algo.category === 'graph') {
    inputRaw.value = JSON.stringify(JSON.parse(algo.defaultInput), null, 2)
  } else if (algo.category === 'tree') {
    inputRaw.value = JSON.stringify(JSON.parse(algo.defaultInput), null, 2)
  }
}

function parseInput(): unknown {
  const algo = selectedAlgo.value
  if (!algo) return {}

  if (algo.id === 'binary-search') {
    return { arr: inputRaw.value.split(',').map(Number), target: Number(extraParam.value) || 0 }
  }
  if (algo.category === 'linked-list') {
    return { values: inputRaw.value.split(',').map(Number), x: Number(extraParam.value) || 0 }
  }
  if (algo.category === 'sorting' || algo.category === 'heap') {
    return { arr: inputRaw.value.split(',').map(Number) }
  }
  if (algo.category === 'graph') {
    return JSON.parse(inputRaw.value)
  }
  if (algo.category === 'tree') {
    return JSON.parse(inputRaw.value)
  }
  return JSON.parse(algo.defaultInput)
}

function selectTreePreset(json: unknown) {
  inputRaw.value = JSON.stringify(json, null, 2)
}

function runAlgorithm() {
  const algo = selectedAlgo.value
  if (!algo) return
  try {
    const input = parseInput()
    execAlgorithm(algo, input)
  } catch {
    // input parse error — ignore, show default
    execAlgorithm(algo, JSON.parse(algo.defaultInput))
  }
}

// ── SVG viewBox helpers ──

const svgViewBox = computed(() => {
  const step = currentStep.value
  if (!step) return '0 0 700 300'
  if (step.visualType === 'array') return '0 0 700 260'
  if (step.visualType === 'linked-list') return '0 0 700 140'
  if (step.visualType === 'tree') return '-260 0 700 340'
  if (step.visualType === 'graph') return '-180 -170 500 360'
  if (step.visualType === 'heap') return '0 0 700 280'
  return '0 0 700 300'
})

const compareAlgo = computed(() => algorithmRegistry.find(a => a.id === compareId.value) || null)

function runCompare() {
  if (!selectedAlgo.value || !compareAlgo.value) return

  // Run selected algorithm
  try {
    const input = parseInput()
    execAlgorithm(selectedAlgo.value, input)
  } catch {
    execAlgorithm(selectedAlgo.value, JSON.parse(selectedAlgo.value.defaultInput))
  }

  // Run comparison algorithm and count steps
  try {
    const input2 = parseInput()
    const gen2 = compareAlgo.value.generateSteps(input2)
    let count = 0
    for (const _ of gen2) count++
    compareSteps.value = count
    compareResult.value = `${compareAlgo.value.name}：${count} 步`
  } catch (e: any) {
    compareResult.value = `执行失败: ${e?.message || ''}`
  }
}

async function requestAIExplanation() {
  const step = currentStep.value
  const algo = selectedAlgo.value
  if (!step || !algo) return
  aiLoading.value = true
  aiExplanation.value = ''
  try {
    const res = await apiClient.post('/chat/message', {
      message: `你是一个408考研算法导师。请用1-2句中文解释这个算法步骤的含义：\n算法：${algo.name}\n步骤：${step.description}\n当前变量：${JSON.stringify(step.variables)}`,
      mode: 'guided',
    })
    aiExplanation.value = res.data?.reply || res.data?.message || '暂无解释'
  } catch {
    aiExplanation.value = 'AI 讲解暂不可用，请稍后重试'
  } finally {
    aiLoading.value = false
  }
}

// ── Tree Builder helpers ──
function addTreeNode(parentIdx: number, side: 'left' | 'right') {
  try {
    const tree = JSON.parse(inputRaw.value)
    function findAndAdd(node: any, idx: number): boolean {
      if (idx === 0) {
        if (side === 'left' && !node.left) node.left = { value: 0, left: null, right: null }
        else if (side === 'right' && !node.right) node.right = { value: 0, left: null, right: null }
        else return false
        return true
      }
      if (node.left && findAndAdd(node.left, idx - 1)) return true
      if (node.right) {
        const leftCount = countNodes(node.left)
        if (findAndAdd(node.right, idx - 1 - leftCount)) return true
      }
      return false
    }
    function countNodes(n: any): number {
      if (!n) return 0
      return 1 + countNodes(n.left) + countNodes(n.right)
    }
    findAndAdd(tree, parentIdx)
    inputRaw.value = JSON.stringify(tree, null, 2)
  } catch { /* ignore */ }
}

function removeTreeNode(idx: number) {
  try {
    const tree = JSON.parse(inputRaw.value)
    if (idx === 0) {
      inputRaw.value = JSON.stringify({ value: 0, left: null, right: null }, null, 2)
      return
    }
    function findAndRemove(node: any, target: number, current: { v: number }): boolean {
      if (node.left) {
        if (current.v + 1 === target) { node.left = null; return true }
        current.v++
        if (findAndRemove(node.left, target, current)) return true
      }
      if (node.right) {
        if (current.v + 1 === target) { node.right = null; return true }
        current.v++
        if (findAndRemove(node.right, target, current)) return true
      }
      return false
    }
    findAndRemove(tree, idx, { v: 0 })
    inputRaw.value = JSON.stringify(tree, null, 2)
  } catch { /* ignore */ }
}

// ── Init ──

onMounted(() => {
  selectAlgorithm(selectedId.value)
})
</script>

<template>
  <div class="visual-view animate-fade-in-up pb-20 lg:pb-0">
    <!-- Header -->
    <div class="flex items-center gap-4 mb-5">
      <button class="back-btn" @click="router.back()">
        <ArrowLeft :size="19" />
      </button>
      <h2 class="text-lg font-bold text-text-primary">代码可视化</h2>

      <!-- Algorithm Selector -->
      <div class="relative ml-auto">
        <button
          class="algo-select-btn"
          @click="showAlgoMenu = !showAlgoMenu"
        >
          <Code2 :size="14" />
          <span>{{ selectedAlgo?.name || '选择算法' }}</span>
          <ChevronDown :size="14" :class="{ 'rotate-180': showAlgoMenu }" style="transition: transform 0.2s" />
        </button>

        <transition name="menu-fade">
          <div v-if="showAlgoMenu" class="algo-dropdown">
            <div
              v-for="group in algorithmsByCategory"
              :key="group.category"
            >
              <p class="text-[10px] font-semibold uppercase tracking-wider px-3 py-2 text-text-muted">
                {{ group.label }}
              </p>
              <button
                v-for="algo in group.algos"
                :key="algo.id"
                :class="['algo-option', { active: selectedId === algo.id }]"
                @click="selectAlgorithm(algo.id)"
              >
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-text-primary truncate">{{ algo.name }}</p>
                  <p class="text-xs text-text-tertiary">{{ algo.timeComplexity }}</p>
                </div>
                <div v-if="selectedId === algo.id" class="w-2 h-2 rounded-full bg-primary-500 flex-shrink-0" />
              </button>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Click backdrop to close dropdown -->
    <div v-if="showAlgoMenu" class="fixed inset-0 z-10" @click="showAlgoMenu = false" />

    <!-- Algorithm Info -->
    <div class="flex items-center gap-3 mb-4 ml-1 flex-wrap">
      <p class="text-sm text-text-tertiary">{{ selectedAlgo?.description }}</p>
      <button
        :class="['compare-toggle', { active: compareMode }]"
        @click="compareMode = !compareMode; if (!compareMode) { compareSteps.value = 0; compareResult.value = '' }"
      >
        对比模式
      </button>
      <!-- Second algo selector when compare mode is on -->
      <select
        v-if="compareMode"
        v-model="compareId"
        class="compare-select text-xs"
      >
        <option value="" disabled>选择对比算法...</option>
        <option v-for="a in algorithmRegistry.filter(x => x.id !== selectedId)" :key="a.id" :value="a.id">
          {{ a.name }} ({{ a.timeComplexity }})
        </option>
      </select>
    </div>

    <!-- Input Area -->
    <div class="glass-card rounded-2xl p-4 mb-4">
      <div class="flex items-end gap-3 flex-wrap">
        <div class="flex-1 min-w-[200px]">
          <label class="text-xs font-medium text-text-secondary mb-1.5 block">
            {{ selectedAlgo?.inputLabel || '输入数据' }}
          </label>
          <textarea
            v-if="selectedAlgo?.category === 'tree' || selectedAlgo?.category === 'graph'"
            v-model="inputRaw"
            rows="4"
            class="input-code w-full rounded-xl px-3 py-2 text-sm font-mono resize-none outline-none transition-all"
            spellcheck="false"
          />
          <input
            v-else
            v-model="inputRaw"
            :placeholder="selectedAlgo?.inputHint || ''"
            class="input-code w-full rounded-xl px-3 py-2 text-sm font-mono outline-none transition-all"
            @keydown.enter="runAlgorithm"
          />
        </div>

        <div v-if="needsExtraParam" class="w-28">
          <label class="text-xs font-medium text-text-secondary mb-1.5 block">{{ extraParamLabel }}</label>
          <input
            v-model="extraParam"
            type="number"
            class="input-code w-full rounded-xl px-3 py-2 text-sm font-mono outline-none transition-all"
            @keydown.enter="runAlgorithm"
          />
        </div>

        <button class="run-btn flex-shrink-0" @click="compareMode && compareAlgo ? runCompare() : runAlgorithm()">
          <Play :size="14" />
          <span>{{ compareMode && compareAlgo ? '对比运行' : '运行' }}</span>
        </button>
      </div>

      <!-- Tree Presets + Builder -->
      <div v-if="selectedAlgo?.category === 'tree'" class="flex items-center gap-2 mt-3 flex-wrap">
        <span class="text-xs text-text-muted">预设树：</span>
        <button
          v-for="(preset, i) in treePresets"
          :key="i"
          class="preset-chip"
          @click="selectTreePreset(preset.json)"
        >
          {{ preset.label }}
        </button>
        <button
          :class="['preset-chip', { active: showTreeBuilder }]"
          @click="showTreeBuilder = !showTreeBuilder"
        >
          建树
        </button>
      </div>

      <!-- Interactive Tree Builder -->
      <div v-if="showTreeBuilder && selectedAlgo?.category === 'tree'" class="tree-builder mt-3 p-3 rounded-xl bg-ink">
        <p class="text-xs text-text-muted mb-2">点击节点按钮添加/删除子节点</p>
        <div class="flex flex-wrap gap-2">
          <template v-for="(node, i) in (() => { try { const t = JSON.parse(inputRaw.value); const nodes: {value: number, idx: number}[] = []; function walk(n: any, id: {v: number}) { if(!n) return; nodes.push({value: n.value, idx: id.v}); id.v++; walk(n.left, id); walk(n.right, id); } walk(t, {v: 0}); return nodes; } catch { return []; } })()" :key="i">
            <div class="tree-node-chip">
              <span class="text-xs font-mono font-bold text-text-primary">{{ node.value }}</span>
              <button class="tn-btn" @click="addTreeNode(node.idx, 'left')" title="添加左子">+L</button>
              <button class="tn-btn" @click="addTreeNode(node.idx, 'right')" title="添加右子">+R</button>
              <button class="tn-btn danger" @click="removeTreeNode(node.idx)" title="删除">×</button>
            </div>
          </template>
        </div>
        <p class="text-[10px] text-text-muted mt-2">编辑节点值请直接修改上方 JSON</p>
      </div>
    </div>

    <!-- Main: Pseudocode + Visualization -->
    <div class="grid grid-cols-1 lg:grid-cols-5 gap-4">
      <!-- Pseudocode Panel -->
      <div class="glass-card rounded-2xl p-4 lg:col-span-2">
        <div class="flex items-center gap-2 mb-3">
          <Code2 :size="14" class="text-text-tertiary" />
          <div class="flex items-center gap-0.5 code-tabs">
            <button :class="['code-tab', { active: codeLang === 'pseudo' }]" @click="codeLang = 'pseudo'">伪代码</button>
            <button :class="['code-tab', { active: codeLang === 'c' }]" @click="codeLang = 'c'">C</button>
            <button :class="['code-tab', { active: codeLang === 'python' }]" @click="codeLang = 'python'">Python</button>
          </div>
        </div>

        <div v-if="!selectedAlgo" class="flex flex-col items-center justify-center py-10 text-text-muted">
          <Code2 :size="36" class="mb-3 opacity-30" />
          <p class="text-sm">选择算法开始</p>
        </div>

        <!-- Pseudocode -->
        <div v-else-if="codeLang === 'pseudo'" class="pseudo-panel">
          <div
            v-for="(line, idx) in selectedAlgo.pseudocode"
            :key="idx"
            :class="['pseudo-line', { active: isPseudoLine(idx) }]"
          >
            <span class="pseudo-line-no">{{ idx + 1 }}</span>
            <span>{{ line }}</span>
          </div>
        </div>

        <!-- C / Python Code -->
        <div v-else class="code-panel">
          <pre class="code-block" :class="codeLang"><code>{{ codeMap[selectedId]?.[codeLang === 'c' ? 'c' : 'python'] || '// 暂无代码' }}</code></pre>
        </div>

        <!-- Variables State -->
        <div
          v-if="currentStep && Object.keys(currentStep.variables).length > 0"
          class="mt-4 pt-3 border-t border-border-light"
        >
          <p class="text-xs font-semibold text-text-tertiary mb-2">当前变量</p>
          <div class="flex flex-wrap gap-1.5">
            <div
              v-for="(val, key) in currentStep.variables"
              :key="key"
              class="var-chip"
            >
              <span class="text-amber-400 font-mono text-xs">{{ key }}</span>
              <span class="text-text-muted text-xs">=</span>
              <span class="text-text-primary font-mono text-xs">{{ val }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Visualization Panel -->
      <div class="glass-card rounded-2xl p-4 lg:col-span-3 overflow-hidden">
        <p class="text-xs font-semibold text-text-secondary mb-2 tracking-wide">
          可视化 {{ currentStep ? `· 步骤 ${currentIndex + 1}/${totalSteps}` : '' }}
        </p>

        <div v-if="error" class="error-box">
          <p class="font-medium mb-1 text-sm">执行失败</p>
          <p class="text-xs">{{ error }}</p>
          <button class="mt-2 px-3 py-1 rounded-lg bg-red-100 text-red-600 text-xs font-medium hover:bg-red-200 transition-colors" @click="runAlgorithm">
            重试
          </button>
        </div>

        <div v-else-if="isRunning" class="flex flex-col items-center justify-center py-16">
          <Zap :size="32" class="text-amber-400 animate-pulse mb-3" />
          <p class="text-sm text-text-tertiary">生成动画步骤中...</p>
        </div>

        <div v-else-if="!steps.length" class="flex flex-col items-center justify-center py-16">
          <Code2 :size="40" class="text-text-muted opacity-30 mb-3" />
          <p class="text-sm text-text-muted">选择算法，点击「运行」</p>
        </div>

        <!-- SVG Canvas -->
        <div v-else class="viz-canvas">
          <svg :viewBox="svgViewBox" class="w-full max-h-[380px]">

            <!-- ═══ Array Visualization ═══ -->
            <g v-if="currentStep?.visualType === 'array'">
              <!-- Bars -->
              <g v-for="(el, i) in (currentStep.elements as ArrayElement[])" :key="i">
                <rect
                  :x="i * 50 + 30"
                  :y="220 - el.value * 18"
                  :width="36"
                  :height="el.value * 18"
                  :rx="4"
                  :class="[
                    'bar',
                    el.status === 'default' && 'bar-default',
                    el.status === 'pivot' && 'bar-pivot',
                    el.status === 'comparing' && 'bar-comparing',
                    el.status === 'swapped' && 'bar-swapped',
                    el.status === 'sorted' && 'bar-sorted',
                  ]"
                />
                <!-- Index highlight ring -->
                <rect
                  v-if="currentStep.highlights.includes(i)"
                  :x="i * 50 + 28"
                  :y="218 - el.value * 18"
                  :width="40"
                  :height="el.value * 18 + 4"
                  :rx="6"
                  fill="none"
                  stroke="currentColor"
                  :class="el.status === 'pivot' ? 'text-amber-400' : el.status === 'comparing' ? 'text-blue-400' : el.status === 'swapped' ? 'text-rose-400' : 'text-violet-400'"
                  stroke-width="2.5"
                  stroke-dasharray="4 2"
                />
                <!-- Index label -->
                <text :x="i * 50 + 48" y="248" text-anchor="middle" class="text-[10px] fill-text-muted">{{ i }}</text>
                <!-- Value label -->
                <text :x="i * 50 + 48" :y="218 - el.value * 18 - 6" text-anchor="middle" class="text-[11px] font-mono font-semibold" :fill="el.status === 'sorted' ? '#10b981' : el.status === 'pivot' ? '#f59e0b' : el.status === 'swapped' ? '#e11d48' : '#a78bfa'">{{ el.value }}</text>
              </g>
            </g>

            <!-- ═══ Linked List Visualization ═══ -->
            <g v-if="currentStep?.visualType === 'linked-list'">
              <template v-for="(node, i) in (currentStep.elements as ListNode[])" :key="i">
                <!-- Arrow from previous node -->
                <line
                  v-if="i > 0"
                  :x1="i * 120 - 24"
                  y1="60"
                  :x2="i * 120"
                  y2="60"
                  stroke="var(--color-text-muted)"
                  stroke-width="2"
                  marker-end="url(#arrowhead)"
                />
                <!-- Node box -->
                <rect
                  :x="i * 120 + 2"
                  y="30"
                  width="60"
                  height="40"
                  :rx="8"
                  :fill="node.status === 'cur' ? 'rgba(245,158,11,0.2)' : node.status === 'pre' ? 'rgba(96,165,250,0.2)' : node.status === 'deleted' ? 'rgba(225,29,72,0.15)' : 'var(--color-bg-secondary)'"
                  :stroke="node.status === 'cur' ? 'rgba(245,158,11,0.5)' : node.status === 'pre' ? 'rgba(96,165,250,0.5)' : node.status === 'deleted' ? 'rgba(225,29,72,0.4)' : 'var(--color-border)'"
                  stroke-width="1.5"
                />
                <!-- Value -->
                <text
                  :x="i * 120 + 32"
                  y="56"
                  text-anchor="middle"
                  :class="node.status === 'deleted' ? 'line-through' : ''"
                  :fill="node.status === 'deleted' ? 'var(--color-text-muted)' : node.status === 'cur' ? '#f59e0b' : 'var(--color-text-primary)'"
                  class="text-sm font-mono font-semibold"
                >{{ node.value }}</text>
                <!-- Status label -->
                <text
                  v-if="node.status !== 'default'"
                  :x="i * 120 + 32"
                  y="24"
                  text-anchor="middle"
                  class="text-[10px] font-semibold"
                  :fill="node.status === 'cur' ? '#f59e0b' : node.status === 'pre' ? '#60a5fa' : '#e11d48'"
                >{{ node.status === 'cur' ? 'cur' : node.status === 'pre' ? 'pre' : '×' }}</text>
                <!-- Index label -->
                <text :x="i * 120 + 32" y="82" text-anchor="middle" class="text-[10px] fill-text-muted">{{ i }}</text>
              </template>
              <!-- NULL marker -->
              <text
                v-if="(currentStep.elements as ListNode[]).length > 0"
                :x="(currentStep.elements as ListNode[]).length * 120 + 10"
                y="56"
                class="text-xs font-mono fill-text-muted"
              >NULL</text>

              <defs>
                <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
                  <polygon points="0 0, 8 3, 0 6" fill="var(--color-text-muted)" />
                </marker>
              </defs>
            </g>

            <!-- ═══ Tree Visualization ═══ -->
            <g v-if="currentStep?.visualType === 'tree'">
              <template v-for="(node, i) in (currentStep.elements as TreeNode[])" :key="i">
                <!-- Edge to left child -->
                <line
                  v-if="node.left !== null"
                  :x1="node.x"
                  :y1="node.y * 80 + 30"
                  :x2="(currentStep.elements as TreeNode[])[node.left].x"
                  :y2="(currentStep.elements as TreeNode[])[node.left].y * 80 + 30"
                  stroke="var(--color-border-strong)"
                  stroke-width="1.5"
                />
                <!-- Edge to right child -->
                <line
                  v-if="node.right !== null"
                  :x1="node.x"
                  :y1="node.y * 80 + 30"
                  :x2="(currentStep.elements as TreeNode[])[node.right].x"
                  :y2="(currentStep.elements as TreeNode[])[node.right].y * 80 + 30"
                  stroke="var(--color-border-strong)"
                  stroke-width="1.5"
                />
              </template>

              <template v-for="(node, i) in (currentStep.elements as TreeNode[])" :key="'n-' + i">
                <circle
                  :cx="node.x"
                  :cy="node.y * 80 + 30"
                  r="18"
                  :fill="node.status === 'current' ? 'rgba(245,158,11,0.25)' : node.status === 'visited' ? 'rgba(124,58,237,0.2)' : 'var(--color-bg-secondary)'"
                  :stroke="node.status === 'current' ? '#f59e0b' : node.status === 'visited' ? '#7c3aed' : 'var(--color-border-strong)'"
                  stroke-width="2"
                />
                <text
                  :x="node.x"
                  :y="node.y * 80 + 35"
                  text-anchor="middle"
                  :fill="node.status === 'current' ? '#f59e0b' : node.status === 'visited' ? '#a78bfa' : 'var(--color-text-primary)'"
                  class="text-sm font-mono font-bold"
                >{{ node.value }}</text>
              </template>
            </g>

            <!-- ═══ Graph Visualization ═══ -->
            <g v-if="currentStep?.visualType === 'graph'">
              <!-- Edges -->
              <g v-for="(edge, ei) in (currentStep.edges || [])" :key="'e-' + ei">
                <line
                  :x1="(currentStep.elements as any)[edge.from]?.x || 0"
                  :y1="(currentStep.elements as any)[edge.from]?.y || 0"
                  :x2="(currentStep.elements as any)[edge.to]?.x || 0"
                  :y2="(currentStep.elements as any)[edge.to]?.y || 0"
                  :stroke="edge.status === 'active' ? '#f59e0b' : edge.status === 'considered' ? '#60a5fa' : edge.status === 'shortest' ? '#10b981' : 'var(--color-border-strong)'"
                  :stroke-width="edge.status === 'shortest' ? 3 : edge.status === 'active' ? 2 : 1.2"
                  marker-end="url(#graphArrow)"
                />
                <!-- Edge weight -->
                <text
                  :x="(((currentStep.elements as any)[edge.from]?.x || 0) + ((currentStep.elements as any)[edge.to]?.x || 0)) / 2 + 14"
                  :y="(((currentStep.elements as any)[edge.from]?.y || 0) + ((currentStep.elements as any)[edge.to]?.y || 0)) / 2 - 6"
                  class="text-[10px] font-mono"
                  :fill="edge.status === 'shortest' ? '#10b981' : 'var(--color-text-muted)'"
                >{{ edge.weight }}</text>
              </g>
              <!-- Nodes -->
              <g v-for="(node, i) in (currentStep.elements as any[])" :key="'gn-' + i">
                <circle
                  :cx="node.x"
                  :cy="node.y"
                  r="22"
                  :fill="node.status === 'current' ? 'rgba(245,158,11,0.3)' : node.status === 'visited' ? 'rgba(124,58,237,0.25)' : node.status === 'visiting' ? 'rgba(96,165,250,0.2)' : node.status === 'queued' ? 'rgba(16,185,129,0.15)' : 'var(--color-bg-secondary)'"
                  :stroke="node.status === 'current' ? '#f59e0b' : node.status === 'visited' ? '#7c3aed' : node.status === 'visiting' ? '#60a5fa' : node.status === 'queued' ? '#10b981' : 'var(--color-border-strong)'"
                  :stroke-width="currentStep.highlights.includes(i) ? 3 : 2"
                />
                <text
                  :x="node.x"
                  :y="node.y + 5"
                  text-anchor="middle"
                  :fill="node.status === 'current' ? '#f59e0b' : 'var(--color-text-primary)'"
                  class="text-sm font-bold"
                >{{ node.label }}</text>
                <!-- Distance label for Dijkstra -->
                <text
                  v-if="node.distance !== undefined && node.distance < Infinity"
                  :x="node.x"
                  :y="node.y + 36"
                  text-anchor="middle"
                  :fill="node.status === 'current' ? '#f59e0b' : '#10b981'"
                  class="text-[10px] font-mono font-semibold"
                >{{ node.distance }}</text>
              </g>
              <defs>
                <marker id="graphArrow" markerWidth="8" markerHeight="6" refX="30" refY="3" orient="auto">
                  <polygon points="0 0, 8 3, 0 6" fill="var(--color-text-muted)" />
                </marker>
              </defs>
            </g>

            <!-- ═══ Heap Visualization ═══ -->
            <g v-if="currentStep?.visualType === 'heap'">
              <!-- Tree arcs connecting parent-child -->
              <g v-for="(el, i) in (currentStep.elements as ArrayElement[])" :key="'h-arc-' + i">
                <!-- Left child arc -->
                <path
                  v-if="2 * i + 1 < (currentStep.elements as ArrayElement[]).length"
                  :d="`M ${i * 50 + 48} ${218 - el.value * 18} Q ${i * 50 + 48} ${218 - el.value * 18 - 20}, ${(2 * i + 1) * 50 + 48} ${218 - (currentStep.elements as ArrayElement[])[2 * i + 1].value * 18}`"
                  fill="none"
                  stroke="var(--color-border-strong)"
                  stroke-width="1"
                  stroke-dasharray="3 2"
                  opacity="0.4"
                />
                <!-- Right child arc -->
                <path
                  v-if="2 * i + 2 < (currentStep.elements as ArrayElement[]).length"
                  :d="`M ${i * 50 + 48} ${218 - el.value * 18} Q ${i * 50 + 48} ${218 - el.value * 18 - 20}, ${(2 * i + 2) * 50 + 48} ${218 - (currentStep.elements as ArrayElement[])[2 * i + 2].value * 18}`"
                  fill="none"
                  stroke="var(--color-border-strong)"
                  stroke-width="1"
                  stroke-dasharray="3 2"
                  opacity="0.4"
                />
              </g>
              <!-- Bars (same as array but with heap tree arcs) -->
              <g v-for="(el, i) in (currentStep.elements as ArrayElement[])" :key="i">
                <rect
                  :x="i * 50 + 30"
                  :y="218 - el.value * 18"
                  :width="36"
                  :height="el.value * 18"
                  :rx="4"
                  :class="[
                    'bar',
                    el.status === 'default' && 'bar-default',
                    el.status === 'pivot' && 'bar-pivot',
                    el.status === 'comparing' && 'bar-comparing',
                    el.status === 'swapped' && 'bar-swapped',
                    el.status === 'sorted' && 'bar-sorted',
                  ]"
                />
                <rect
                  v-if="currentStep.highlights.includes(i)"
                  :x="i * 50 + 28"
                  :y="218 - el.value * 18"
                  :width="40"
                  :height="el.value * 18 + 4"
                  :rx="6"
                  fill="none"
                  stroke="currentColor"
                  :class="el.status === 'pivot' ? 'text-amber-400' : el.status === 'comparing' ? 'text-blue-400' : el.status === 'swapped' ? 'text-rose-400' : 'text-violet-400'"
                  stroke-width="2.5"
                  stroke-dasharray="4 2"
                />
                <text :x="i * 50 + 48" y="248" text-anchor="middle" class="text-[10px] fill-text-muted">{{ i }}</text>
                <text :x="i * 50 + 48" :y="218 - el.value * 18 - 6" text-anchor="middle" class="text-[11px] font-mono font-semibold" :fill="el.status === 'sorted' ? '#10b981' : el.status === 'pivot' ? '#f59e0b' : el.status === 'swapped' ? '#e11d48' : '#a78bfa'">{{ el.value }}</text>
              </g>
            </g>
          </svg>
        </div>

        <!-- Step Description -->
        <div v-if="currentStep" class="step-desc mt-3">
          <span class="text-xs font-semibold text-amber-600 mr-2">Step {{ currentIndex + 1 }}</span>
          <span class="text-sm text-text-primary">{{ currentStep.description }}</span>
          <button
            v-if="!aiLoading && !aiExplanation"
            class="ai-explain-btn ml-2"
            @click="requestAIExplanation"
          >
            AI 讲解
          </button>
          <span v-if="aiLoading" class="text-xs text-text-muted ml-2">AI 思考中...</span>
        </div>
        <!-- AI Explanation -->
        <div v-if="aiExplanation" class="ai-explain-box mt-2">
          <p class="text-xs text-amber-600 font-semibold mb-1">AI 讲解</p>
          <p class="text-xs text-text-secondary">{{ aiExplanation }}</p>
          <button class="text-[10px] text-text-muted mt-1" @click="aiExplanation = ''">收起</button>
        </div>
      </div>
    </div>

    <!-- Comparison Result -->
    <div v-if="compareMode && compareResult" class="glass-card rounded-2xl p-4 mt-4">
      <div class="flex items-center gap-4">
        <div class="flex-1 text-center">
          <p class="text-xs text-text-muted mb-1">{{ selectedAlgo?.name }}</p>
          <p class="text-lg font-bold text-primary-500">{{ totalSteps }} 步</p>
          <p class="text-xs text-text-tertiary">{{ selectedAlgo?.timeComplexity }}</p>
        </div>
        <div class="text-2xl font-bold text-text-muted">VS</div>
        <div class="flex-1 text-center">
          <p class="text-xs text-text-muted mb-1">{{ compareAlgo?.name }}</p>
          <p class="text-lg font-bold text-amber-500">{{ compareSteps }} 步</p>
          <p class="text-xs text-text-tertiary">{{ compareAlgo?.timeComplexity }}</p>
        </div>
      </div>
      <div class="mt-2 pt-2 border-t border-border-light text-center">
        <p class="text-xs text-text-secondary">
          {{ totalSteps < compareSteps ? `${selectedAlgo?.name} 步数更少` : totalSteps > compareSteps ? `${compareAlgo?.name} 步数更少` : '步数相同' }}
        </p>
      </div>
    </div>

    <!-- Playback Controls -->
    <div v-if="steps.length > 0" class="glass-card rounded-2xl p-4 mt-4">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1">
          <!-- Speed selector -->
          <div class="flex items-center gap-0.5">
            <button
              v-for="opt in speedOptions"
              :key="opt.value"
              :class="['speed-chip', { active: speed === opt.value }]"
              @click="setSpeed(opt.value)"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button class="ctrl-btn" @click="stepBack" :disabled="currentIndex === 0">
            <SkipBack :size="17" />
          </button>
          <button class="ctrl-btn" @click="reset">
            <RotateCcw :size="15" />
          </button>
          <button class="play-btn-lg" @click="togglePlay">
            <component :is="isPlaying ? Pause : Play" :size="20" class="text-white ml-0.5" />
          </button>
          <button class="ctrl-btn" @click="stepForward" :disabled="playerIsComplete">
            <SkipForward :size="17" />
          </button>
        </div>

        <div class="flex items-center gap-2 min-w-[80px] justify-end">
          <span class="text-xs font-mono font-semibold text-text-secondary">
            {{ currentIndex + 1 }} / {{ totalSteps }}
          </span>
        </div>
      </div>

      <!-- Progress Bar -->
      <div class="progress-track mt-3">
        <div class="progress-fill" :style="{ width: `${progress}%` }" />
      </div>
    </div>

    <!-- 408 真题链接 -->
    <div v-if="selectedAlgo && getQuestionsForAlgo(selectedId).length > 0" class="glass-card rounded-2xl p-4 mt-4">
      <p class="text-xs font-semibold text-text-secondary mb-3 tracking-wide">408 真题练习</p>
      <div class="space-y-2">
        <div
          v-for="(q, qi) in getQuestionsForAlgo(selectedId)"
          :key="qi"
          class="exam-link"
        >
          <span class="text-xs font-mono text-amber-500 mr-2">{{ q.year }}.#{{ q.number }}</span>
          <span class="text-xs text-text-secondary">{{ q.description }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Layout ── */
.visual-view {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0.5rem 1rem;
}

/* ── Back Button ── */
.back-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
  color: var(--color-text-secondary);
}
.back-btn:hover {
  background: var(--color-bg-secondary);
}

/* ── Algo Select ── */
.algo-select-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-primary);
  background: var(--surface-paper-bg);
  border: 1px solid var(--color-border);
  cursor: pointer;
  position: relative;
  z-index: 20;
}
.algo-select-btn:hover {
  background: var(--color-bg-secondary);
}

.algo-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  width: 240px;
  max-height: 360px;
  overflow-y: auto;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  box-shadow: var(--shadow-md);
  z-index: 30;
  padding: 6px 0;
}

.algo-option {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  text-align: left;
  transition: background 0.15s;
  border: none;
  background: transparent;
  cursor: pointer;
}
.algo-option:hover {
  background: var(--color-bg-secondary);
}
.algo-option.active {
  background: rgba(124, 58, 237, 0.06);
}

.menu-fade-enter-active,
.menu-fade-leave-active {
  transition: opacity 0.15s, transform 0.15s;
}
.menu-fade-enter-from,
.menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.rotate-180 {
  transform: rotate(180deg);
}

/* ── Input ── */
.input-code {
  background: var(--color-bg-ink);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-family: 'SF Mono', 'Fira Code', monospace;
}
.input-code:focus {
  border-color: var(--color-primary-400);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.08);
}
.input-code::placeholder {
  color: var(--color-text-muted);
}

.run-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 22px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.25);
  white-space: nowrap;
}
.run-btn:hover {
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.35);
}
.run-btn:active {
  transform: scale(0.96);
}

.preset-chip {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all 0.15s;
}
.preset-chip:hover {
  border-color: var(--color-primary-400);
  color: var(--color-primary-500);
  background: rgba(124, 58, 237, 0.06);
}

/* ── Pseudocode ── */
.pseudo-panel {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.8rem;
  line-height: 2;
}

.pseudo-line {
  display: flex;
  gap: 12px;
  padding: 2px 8px;
  border-radius: 6px;
  transition: background 0.2s, color 0.2s;
  color: var(--color-text-secondary);
}
.pseudo-line.active {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
  font-weight: 600;
}

.pseudo-line-no {
  width: 20px;
  text-align: right;
  color: var(--color-text-muted);
  flex-shrink: 0;
  font-size: 0.7rem;
  user-select: none;
}

.var-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 6px;
  background: var(--color-bg-ink);
  border: 1px solid var(--color-border);
}

/* ── Code Tabs ── */
.code-tabs {
  background: var(--color-bg-secondary);
  border-radius: 8px;
  padding: 2px;
}
.code-tab {
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.code-tab:hover {
  color: var(--color-text-secondary);
}
.code-tab.active {
  background: var(--color-bg-primary);
  color: var(--color-primary-500);
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}

.code-panel {
  max-height: 340px;
  overflow-y: auto;
}
.code-block {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 0.72rem;
  line-height: 1.6;
  color: var(--color-text-secondary);
  background: var(--color-bg-ink);
  border-radius: 10px;
  padding: 12px 14px;
  margin: 0;
  white-space: pre;
  overflow-x: auto;
}
.code-block.c {
  color: #60a5fa;
}
.code-block.python {
  color: #10b981;
}

/* ── Error ── */
.error-box {
  border-radius: 12px;
  padding: 16px;
  background: rgba(225, 29, 72, 0.06);
  border: 1px solid rgba(225, 29, 72, 0.15);
  color: var(--color-danger-500);
}

/* ── SVG Canvas ── */
.viz-canvas {
  background: var(--color-bg-ink);
  border-radius: 12px;
  overflow: hidden;
}

/* Bars */
.bar {
  transition: y 0.5s ease, height 0.5s ease, fill 0.3s, opacity 0.3s;
}

.bar-default { fill: var(--color-primary-400); opacity: 0.6; }
.bar-pivot { fill: #f59e0b; opacity: 0.85; }
.bar-comparing { fill: #60a5fa; opacity: 0.8; }
.bar-swapped { fill: #e11d48; opacity: 0.85; }
.bar-sorted { fill: #10b981; opacity: 0.8; }

/* ── Step Description ── */
.step-desc {
  display: flex;
  align-items: baseline;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.08);
}

/* ── Playback ── */
.speed-chip {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.15s;
}
.speed-chip:hover {
  color: var(--color-text-secondary);
}
.speed-chip.active {
  color: var(--color-primary-500);
  background: rgba(124, 58, 237, 0.08);
}

.ctrl-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.15s;
}
.ctrl-btn:hover:not(:disabled) {
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}
.ctrl-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.play-btn-lg {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #7c3aed, #5b21b6);
  border: none;
  cursor: pointer;
  box-shadow: 0 3px 12px rgba(124, 58, 237, 0.3);
  transition: transform 0.15s, box-shadow 0.2s;
}
.play-btn-lg:hover {
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}
.play-btn-lg:active {
  transform: scale(0.93);
}

.progress-track {
  width: 100%;
  height: 4px;
  background: var(--color-bg-secondary);
  border-radius: 99px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #a78bfa);
  border-radius: 99px;
  transition: width 0.3s ease;
}

/* ── Tree Builder ── */
.tree-builder {
  background: var(--color-bg-ink);
  border: 1px solid var(--color-border);
}
.tree-node-chip {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 8px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
}
.tn-btn {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  background: rgba(124, 58, 237, 0.08);
  color: var(--color-primary-500);
  transition: all 0.12s;
}
.tn-btn:hover { background: rgba(124, 58, 237, 0.18); }
.tn-btn.danger { background: rgba(225, 29, 72, 0.08); color: var(--color-danger-500); }
.tn-btn.danger:hover { background: rgba(225, 29, 72, 0.18); }

/* ── AI Explanation ── */
.ai-explain-btn {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--color-amber-500);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.15);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.ai-explain-btn:hover {
  background: rgba(245, 158, 11, 0.15);
}
.ai-explain-box {
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.04);
  border: 1px solid rgba(245, 158, 11, 0.1);
}

/* ── Exam Questions ── */
.exam-link {
  display: flex;
  align-items: baseline;
  padding: 6px 10px;
  border-radius: 8px;
  transition: background 0.15s;
  cursor: default;
}
.exam-link:hover {
  background: var(--color-bg-secondary);
}

/* ── Comparison ── */
.compare-toggle {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-text-muted);
  background: transparent;
  border: 1.5px dashed var(--color-border);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s;
}
.compare-toggle:hover,
.compare-toggle.active {
  border-color: var(--color-amber-400);
  color: var(--color-amber-500);
  background: rgba(245, 158, 11, 0.06);
}

.compare-select {
  padding: 4px 10px;
  border-radius: 8px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  font-weight: 500;
  cursor: pointer;
  outline: none;
  max-width: 200px;
}

/* ── Responsive ── */
@media (max-width: 1023px) {
  .visual-view {
    padding: 0.5rem;
  }
  .algo-dropdown {
    width: 220px;
    right: -60px;
  }
}
</style>
