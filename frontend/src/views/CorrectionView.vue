<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, Camera, Upload } from 'lucide-vue-next'

const uploadedImage = ref<string | null>(null)

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.[0]) {
    const reader = new FileReader()
    reader.onload = (e) => { uploadedImage.value = e.target?.result as string }
    reader.readAsDataURL(input.files[0])
  }
}
</script>

<template>
  <div class="correction-view animate-fade-in-up">
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">手写批改</h2>
    </div>

    <div
      v-if="!uploadedImage"
      class="glass-card !rounded-2xl p-10 flex flex-col items-center justify-center min-h-[350px] cursor-pointer"
      @click="$refs.fileInput.click()"
    >
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileSelect" />
      <div class="w-20 h-20 rounded-full bg-emerald-50 flex items-center justify-center mb-4">
        <Camera :size="32" style="color: #10B981" />
      </div>
      <p class="text-base font-semibold mb-1" style="color: var(--color-text-primary)">上传草稿纸</p>
      <p class="text-sm" style="color: var(--color-text-tertiary)">AI 将定位你解题步骤中的错误</p>
      <button
        class="mt-6 px-5 py-2.5 rounded-xl text-white text-sm font-medium flex items-center gap-2"
        style="background: linear-gradient(135deg, #10B981 0%, #059669 100%)"
        @click.stop="$refs.fileInput.click()"
      >
        <Upload :size="16" /> 选择图片
      </button>
    </div>

    <div v-else class="space-y-4">
      <div class="glass-card !rounded-2xl p-4">
        <img :src="uploadedImage" alt="草稿" class="w-full rounded-xl max-h-[400px] object-contain mx-auto" />
      </div>
      <p class="text-xs text-center" style="color: var(--color-text-tertiary)">批注功能开发中 (Step 5)</p>
    </div>
  </div>
</template>
