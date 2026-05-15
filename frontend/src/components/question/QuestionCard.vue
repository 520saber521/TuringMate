<script setup lang="ts">
/**
 * QuestionCard - 题目卡片组件
 * 显示识别后的题目信息：科目、知识点标签、难度、题面内容
 */
import type { SubjectType } from '@/types/question'
import TopicTag from './TopicTag.vue'

const props = defineProps<{
  questionId?: string
  subject?: SubjectType | string
  knowledgeTags?: string[]
  difficulty?: number
  content?: string
  imageUrl?: string
  compact?: boolean
}>()

/** 科目颜色映射 */
const subjectColors: Record<string, { bg: string; text: string; label: string }> = {
  '数据结构': { bg: 'bg-blue-50', 'text': 'text-blue-600', label: 'DS' },
  '计组': { bg: 'bg-green-50', 'text': 'text-green-600', label: 'CO' },
  '操作系统': { bg: 'bg-orange-50', 'text': 'text-orange-600', label: 'OS' },
  '网络': { bg: 'bg-cyan-50', 'text': 'text-cyan-600', label: 'CN' },
}

/** 难度显示配置 */
const difficultyConfig = [
  { level: 1, label: '基础', stars: 1, color: 'text-emerald-500' },
  { level: 2, label: '简单', stars: 2, color: 'text-blue-500' },
  { level: 3, label: '中等', stars: 3, color: 'text-yellow-500' },
  { level: 4, label: '困难', stars: 4, color: 'text-orange-500' },
  { level: 5, label: '极难', stars: 5, color: 'text-red-500' },
]

const subjectStyle = () => subjectColors[props.subject || ''] || subjectColors['数据结构']
const difficultyInfo = () => difficultyConfig[(props.difficulty || 3) - 1] || difficultyConfig[2]
</script>

<template>
  <div :class="['question-card glass-card !rounded-2xl overflow-hidden', compact && '!p-4']" v-bind="$attrs">
    <!-- 头部：科目 + 难度 -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span :class="['subject-badge px-2.5 py-1 rounded-lg text-xs font-bold', subjectStyle().bg, subjectStyle().text]">
          {{ subjectStyle().label }}
        </span>
        <span class="font-medium text-sm" style="color: var(--color-text-primary)">
          {{ subject }}
        </span>
      </div>

      <!-- 难度星级 -->
      <div class="flex items-center gap-1">
        <span :class="['text-xs font-medium', difficultyInfo().color]">
          {{ difficultyInfo().label }}
        </span>
        <span class="flex">
          <svg v-for="i in 5" :key="i" class="w-3 h-3" viewBox="0 0 20 20" fill="currentColor">
            <path :fill-opacity="i <= (difficulty || 3) ? '1' : '0.15'"
              d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
          </svg>
        </span>
      </div>
    </div>

    <!-- 知识点标签 -->
    <div v-if="knowledgeTags?.length" class="flex flex-wrap gap-1.5 mb-3">
      <TopicTag v-for="tag in knowledgeTags" :key="tag" :label="tag" />
    </div>

    <!-- 题面内容 -->
    <div class="question-content">
      <p class="leading-relaxed text-sm" style="color: var(--color-text-primary)">
        {{ content }}
      </p>
    </div>

    <!-- 原图缩略图 -->
    <div v-if="imageUrl && !compact" class="mt-3 pt-3 border-t border-gray-100">
      <img :src="imageUrl" alt="原图" class="w-full max-h-[120px] object-cover rounded-lg opacity-80 hover:opacity-100 transition-opacity" />
    </div>
  </div>
</template>

<style scoped>
.question-card { padding: 1.25rem; }

.question-content {
  background: rgba(108, 92, 231, 0.03);
  border-left: 3px solid var(--color-primary);
  border-radius: 0 0.5rem 0.5rem 0;
  padding: 0.875rem 1rem;
}

.subject-badge {
  letter-spacing: 0.05em;
}
</style>
