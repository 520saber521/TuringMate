<script setup lang="ts">
/**
 * TopicTag - 知识点标签组件
 * 用于显示科目的具体知识点，如"线性表"、"链表"、"二叉树遍历"等
 */
defineProps<{
  label: string
  /** 可选变体 */
  variant?: 'default' | 'outline' | 'filled'
}>()

/** 根据知识点名称自动匹配颜色（简单 hash） */
function getTagColor(label: string): { bg: string; text: string } {
  let sum = 0
  for (let i = 0; i < label.length; i++) sum += label.charCodeAt(i)
  const colors = [
    { bg: 'bg-purple-50', text: 'text-purple-600' },
    { bg: 'bg-blue-50', text: 'text-blue-600' },
    { bg: 'bg-emerald-50', text: 'text-emerald-600' },
    { bg: 'bg-amber-50', text: 'text-amber-600' },
    { bg: 'bg-rose-50', text: 'text-rose-600' },
    { bg: 'bg-indigo-50', text: 'text-indigo-600' },
    { bg: 'bg-teal-50', text: 'text-teal-600' },
  ]
  return colors[sum % colors.length]
}
</script>

<template>
  <span
    :class="[
      'topic-tag inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium transition-colors',
      variant === 'outline' ? 'border' : '',
      variant === 'filled' ? '' : '',
      variant === 'default' ? getTagColor(label).bg + ' ' + getTagColor(label).text : '',
      variant === 'outline' ? 'border-gray-200 text-gray-600 hover:bg-gray-50' : '',
      variant === 'filled' ? 'bg-purple-100 text-purple-700' : '',
    ]"
  >
    {{ label }}
  </span>
</template>
