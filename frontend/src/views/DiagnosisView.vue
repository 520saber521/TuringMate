<script setup lang="ts">
/**
 * DiagnosisView - 薄弱点诊断页面
 * 四科能力雷达图 + 薄弱知识点列表 + 练习推荐
 * 接入后端诊断 API + ECharts 雷达图
 */
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, TrendingDown, BookOpen, Target, ChevronRight } from 'lucide-vue-next'
import { use } from 'echarts/core'
import { RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'
import { getDiagnosisReport, type DiagnosisReportResult, type WeakPoint, type Recommendation } from '@/api/diagnosis'

use([RadarChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const router = useRouter()

const isLoading = ref(false)
const error = ref<string | null>(null)
const scores = ref<Record<string, number>>({})
const weakPoints = ref<WeakPoint[]>([])
const recommendations = ref<Recommendation[]>([])

const activeSubject = ref('all')

onMounted(async () => {
  await loadReport()
})

async function loadReport() {
  isLoading.value = true
  error.value = null

  try {
    const report = await getDiagnosisReport()
    scores.value = report.scores
    weakPoints.value = report.weak_points
    recommendations.value = report.recommendations
  } catch (err: any) {
    error.value = err?.response?.data?.detail || err?.message || '获取报告失败'
    console.error('[DiagnosisView] loadReport failed:', err)
    // 使用 fallback 数据
    scores.value = { '数据结构': 72, '计组': 65, '操作系统': 78, '网络': 58 }
    weakPoints.value = [
      { subject: '计算机网络', topic: 'TCP拥塞控制', score: 45, description: '慢开始、拥塞避免、快重传的阈值变化规律掌握不牢' },
      { subject: '计算机组成原理', topic: '流水线冒险', score: 52, description: '数据冒险、控制冒险的解决策略混淆' },
    ]
    recommendations.value = [
      { type: '专项练习', title: 'TCP 拥塞控制专项训练', count: 10 },
      { type: '知识点回顾', title: '流水线冒险机制详解', count: 1 },
    ]
  } finally {
    isLoading.value = false
  }
}

// ECharts 雷达图配置
const radarOption = computed(() => {
  const subjects = Object.keys(scores.value)
  const values = Object.values(scores.value)

  if (!subjects.length) return {}

  return {
    tooltip: { trigger: 'item' },
    radar: {
      indicator: subjects.map(s => ({ name: s, max: 100 })),
      shape: 'polygon',
      splitNumber: 4,
      axisName: {
        color: '#4B4580',
        fontSize: 12,
        fontWeight: 500,
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(108,92,231,0.02)', 'rgba(108,92,231,0.04)', 'rgba(108,92,231,0.06)', 'rgba(108,92,231,0.08)'],
        },
      },
      axisLine: { lineStyle: { color: 'rgba(108,92,231,0.15)' } },
      splitLine: { lineStyle: { color: 'rgba(108,92,231,0.1)' } },
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '能力评分',
        areaStyle: {
          color: 'rgba(108, 92, 231, 0.15)',
        },
        lineStyle: {
          color: '#6C5CE7',
          width: 2,
        },
        itemStyle: {
          color: '#6C5CE7',
          borderColor: '#fff',
          borderWidth: 2,
        },
      }],
    }],
  }
})

// 科目标签页
const subjectTabs = [
  { key: 'all', label: '全部' },
  { key: '数据结构', label: '数据结构' },
  { key: '计组', label: '计组' },
  { key: '操作系统', label: '操作系统' },
  { key: '网络', label: '网络' },
]

const filteredWeakPoints = computed(() => {
  if (activeSubject.value === 'all') return weakPoints.value
  return weakPoints.value.filter(wp => wp.subject === activeSubject.value)
})

function getScoreColor(score: number): string {
  if (score >= 80) return '#10B981'
  if (score >= 60) return '#F59E0B'
  return '#EF4444'
}
</script>

<template>
  <div class="diagnosis-view animate-fade-in-up pb-20 lg:pb-0">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors" @click="router.back()">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">薄弱点诊断</h2>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="glass-card !rounded-2xl p-8 flex flex-col items-center justify-center">
      <div class="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mb-4">
        <TrendingDown :size="24" class="text-purple-500 animate-pulse" />
      </div>
      <p class="font-semibold text-base mb-1" style="color: var(--color-text-primary)">正在生成诊断报告...</p>
      <p class="text-xs" style="color: var(--color-text-tertiary)">AI 正在分析你的练习数据</p>
    </div>

    <template v-else>
      <!-- Radar Chart -->
      <div class="glass-card !rounded-2xl p-4 mb-4">
        <p class="text-sm font-semibold mb-2" style="color: var(--color-text-primary)">四科能力雷达图</p>
        <div class="w-full h-[280px]">
          <VChart v-if="Object.keys(scores).length" :option="radarOption" autoresize />
          <div v-else class="flex items-center justify-center h-full">
            <p class="text-sm" style="color: var(--color-text-tertiary)">暂无诊断数据</p>
          </div>
        </div>
        <!-- Score Summary -->
        <div class="grid grid-cols-4 gap-2 mt-2">
          <div v-for="(score, subject) in scores" :key="subject" class="text-center">
            <p class="text-xs" style="color: var(--color-text-tertiary)">{{ subject }}</p>
            <p class="text-lg font-bold" :style="{ color: getScoreColor(score) }">{{ score }}</p>
          </div>
        </div>
      </div>

      <!-- Subject Tabs -->
      <div class="flex gap-2 mb-3 overflow-x-auto scrollbar-hide">
        <button
          v-for="tab in subjectTabs"
          :key="tab.key"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all',
            activeSubject === tab.key
              ? 'gradient-primary text-white shadow-sm'
              : 'bg-gray-50 text-gray-600 hover:bg-purple-50'
          ]"
          @click="activeSubject = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Weak Points -->
      <div class="mb-4">
        <h3 class="text-base font-semibold mb-3" style="color: var(--color-text-primary)">薄弱知识点</h3>
        <div v-if="filteredWeakPoints.length" class="space-y-3">
          <div
            v-for="(wp, idx) in filteredWeakPoints"
            :key="idx"
            class="glass-card !rounded-xl p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <span
                class="px-2 py-0.5 rounded-md text-xs font-medium"
                :style="{
                  background: wp.score < 60 ? 'rgba(239,68,68,0.1)' : 'rgba(245,158,11,0.1)',
                  color: wp.score < 60 ? '#EF4444' : '#F59E0B'
                }"
              >
                {{ wp.subject }}
              </span>
              <span class="text-xs font-bold" :style="{ color: getScoreColor(wp.score) }">{{ wp.score }}分</span>
            </div>
            <p class="text-sm font-medium mb-1" style="color: var(--color-text-primary)">{{ wp.topic }}</p>
            <p v-if="wp.description" class="text-xs leading-relaxed" style="color: var(--color-text-tertiary)">{{ wp.description }}</p>
          </div>
        </div>
        <div v-else class="text-center py-6">
          <p class="text-sm" style="color: var(--color-text-tertiary)">该科目暂无薄弱点数据</p>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="recommendations.length" class="mb-4">
        <h3 class="text-base font-semibold mb-3" style="color: var(--color-text-primary)">练习推荐</h3>
        <div class="space-y-2">
          <div
            v-for="(rec, idx) in recommendations"
            :key="idx"
            class="glass-card !rounded-xl p-4 flex items-center gap-3 cursor-pointer hover:shadow-lg transition-shadow"
          >
            <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
              :style="{ background: rec.type === '专项练习' ? 'rgba(108,92,231,0.1)' : rec.type === '知识点回顾' ? 'rgba(59,130,246,0.1)' : 'rgba(245,158,11,0.1)' }"
            >
              <component :is="rec.type === '专项练习' ? Target : BookOpen" :size="18"
                :style="{ color: rec.type === '专项练习' ? '#6C5CE7' : rec.type === '知识点回顾' ? '#3B82F6' : '#F59E0B' }"
              />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--color-text-primary)">{{ rec.title }}</p>
              <p class="text-xs" style="color: var(--color-text-tertiary)">{{ rec.type }} · {{ rec.count }}题</p>
            </div>
            <ChevronRight :size="16" style="color: var(--color-text-tertiary)" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
