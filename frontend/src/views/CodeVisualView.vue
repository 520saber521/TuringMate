<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, Play, Pause, SkipForward, SkipBack } from 'lucide-vue-next'

const sampleCode = ref(`def delete_x(L, x):
    """删除链表中所有值为 x 的结点"""
    pre = L          # 前驱指针
    cur = L.next     # 当前结点
    while cur:
        if cur.data == x:
            pre.next = cur.next
        else:
            pre = cur
        cur = cur.next`)

const isPlaying = ref(false)
const currentStep = ref(0)
const totalSteps = ref(4)
</script>

<template>
  <div class="code-visual-view animate-fade-in-up">
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">代码可视化</h2>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Code Panel -->
      <div class="glass-card !rounded-2xl p-4 overflow-hidden">
        <p class="text-xs font-medium mb-3 px-1" style="color: var(--color-text-secondary)">代码</p>
        <pre class="bg-gray-900 rounded-xl p-4 text-sm leading-relaxed overflow-x-auto"><code style="color: #a78bfa">{{ sampleCode }}</code></pre>
      </div>

      <!-- Visual Panel -->
      <div class="glass-card !rounded-2xl p-4 min-h-[280px] flex items-center justify-center">
        <div class="text-center">
          <p class="text-sm mb-2" style="color: var(--color-text-tertiary)">数据结构动态图示区域</p>
          <!-- TODO: Step 6 - Canvas/SVG visualization -->
          <div class="inline-flex gap-3 mt-4">
            <div v-for="i in 4" :key="i"
              :class="[
                'w-14 h-14 rounded-xl flex items-center justify-center text-xs font-mono transition-all',
                i <= currentStep + 1 ? 'gradient-primary text-white' : 'bg-gray-100'
              ]"
            >
              {{ i === 1 ? 'H' : `N${i-1}` }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Playback Controls -->
    <div class="glass-card !rounded-2xl p-4 mt-4">
      <div class="flex items-center justify-between">
        <span class="text-xs font-medium" style="color: var(--color-text-tertiary)">
          步骤 {{ currentStep + 1 }} / {{ totalSteps }}
        </span>
        <div class="flex items-center gap-2">
          <button class="w-9 h-9 rounded-lg hover:bg-purple-50 flex items-center justify-center transition-colors">
            <SkipBack :size="16" style="color: var(--color-text-secondary)" />
          </button>
          <button
            class="w-11 h-11 rounded-xl gradient-primary flex items-center justify-center shadow-md shadow-purple-200"
            @click="isPlaying = !isPlaying"
          >
            <component :is="isPlaying ? Pause : Play" :size="18" class="text-white ml-0.5" />
          </button>
          <button class="w-9 h-9 rounded-lg hover:bg-purple-50 flex items-center justify-center transition-colors">
            <SkipForward :size="16" style="color: var(--color-text-secondary)" />
          </button>
        </div>
        <span class="text-xs font-medium" style="color: var(--color-text-tertiary)">当前行：{{ currentStep + 2 }}</span>
      </div>
      <!-- Progress Bar -->
      <div class="w-full h-1 bg-gray-100 rounded-full mt-4 overflow-hidden">
        <div
          class="h-full gradient-primary rounded-full transition-all duration-300"
          :style="{ width: `${((currentStep + 1) / totalSteps) * 100}%` }"
        ></div>
      </div>
    </div>
  </div>
</template>
