<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'

const scores = ref({
  '数据结构': 72,
  '计组': 65,
  '操作系统': 78,
  '网络': 58,
})

const weakPoints = ref([
  { subject: '计算机网络', topic: 'TCP拥塞控制', score: 45 },
  { subject: '计算机组成原理', topic: '流水线冒险', score: 52 },
])
</script>

<template>
  <div class="diagnosis-view animate-fade-in-up">
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">薄弱点诊断</h2>
    </div>

    <!-- Radar Chart Placeholder -->
    <div class="glass-card !rounded-2xl p-6 mb-4">
      <p class="text-sm font-semibold mb-4 text-center" style="color: var(--color-text-primary)">四科能力雷达图</p>
      <!-- TODO: Step 5 - ECharts radar chart -->
      <div class="flex items-center justify-center py-8">
        <div class="grid grid-cols-2 gap-3 w-full max-w-xs">
          <div v-for="(score, subject) in scores" :key="subject" class="glass !rounded-xl p-3 text-center">
            <p class="text-xs mb-1" style="color: var(--color-text-tertiary)">{{ subject }}</p>
            <p class="text-lg font-bold gradient-text">{{ score }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Weak Points -->
    <div class="mb-4">
      <h3 class="text-base font-semibold mb-3" style="color: var(--color-text-primary)">薄弱知识点</h3>
      <div class="space-y-3">
        <div
          v-for="(wp, idx) in weakPoints"
          :key="idx"
          class="glass-card !rounded-xl p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="px-2 py-0.5 rounded-md text-xs font-medium bg-red-50 text-red-500">{{ wp.subject }}</span>
            <span class="text-xs font-bold" :style="{ color: wp.score < 60 ? '#EF4444' : '#F59E0B' }">{{ wp.score }}分</span>
          </div>
          <p class="text-sm font-medium" style="color: var(--color-text-primary)">{{ wp.topic }}</p>
        </div>
      </div>
    </div>

    <p class="text-xs text-center pb-20 lg:pb-0" style="color: var(--color-text-tertiary)">
      ECharts 雷达图 + 完整诊断功能开发中 (Step 5)
    </p>
  </div>
</template>
