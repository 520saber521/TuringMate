<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Camera, Upload, Image as ImageIcon, Sparkles, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()
const uploadedImage = ref<string | null>(null)
const isDragging = ref(false)
const isProcessing = ref(false)

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.[0]) {
    previewImage(input.files[0])
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  if (event.dataTransfer?.files?.[0]) {
    previewImage(event.dataTransfer.files[0])
  }
}

function previewImage(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    uploadedImage.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

async function startRecognition() {
  if (!uploadedImage.value) return
  isProcessing.value = true
  // TODO: Call API to recognize question
  setTimeout(() => {
    router.push('/chat/q_mock_001')
    isProcessing.value = false
  }, 1500)
}
</script>

<template>
  <div class="photo-search-view animate-fade-in-up">
    <!-- Header -->
    <div class="flex items-center gap-3 mb-6">
      <button class="w-10 h-10 rounded-xl hover:bg-purple-50 flex items-center justify-center transition-colors" @click="router.back()">
        <ArrowLeft :size="20" style="color: var(--color-text-secondary)" />
      </button>
      <h2 class="text-lg font-bold" style="color: var(--color-text-primary)">拍照搜题</h2>
    </div>

    <!-- Upload Area -->
    <div
      v-if="!uploadedImage"
      :class="[
        'upload-area glass-card !rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-all duration-200 min-h-[320px]',
        isDragging ? '!border-purple-400 bg-purple-50/30' : ''
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
    >
      <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="handleFileSelect">

      <div class="w-20 h-20 rounded-full bg-purple-50 flex items-center justify-center mb-4">
        <Camera :size="32" style="color: var(--color-primary)" />
      </div>

      <p class="text-base font-semibold mb-2" style="color: var(--color-text-primary)">
        拍照或上传题目
      </p>
      <p class="text-sm text-center max-w-xs" style="color: var(--color-text-tertiary)">
        支持 JPG、PNG 格式，可拖拽图片到此处上传
      </p>

      <div class="flex items-center gap-3 mt-6">
        <button
          class="px-5 py-2.5 rounded-xl gradient-primary text-white text-sm font-medium flex items-center gap-2 shadow-md shadow-purple-200"
          @click.stop="$refs.fileInput.click()"
        >
          <Camera :size="16" />
          拍照
        </button>
        <button
          class="px-5 py-2.5 rounded-xl border border-gray-200 text-sm font-medium flex items-center gap-2 hover:bg-gray-50 transition-colors"
          style="color: var(--color-text-secondary)"
          @click.stop="$refs.fileInput.click()"
        >
          <Upload :size="16" />
          选择图片
        </button>
      </div>
    </div>

    <!-- Image Preview -->
    <div v-else class="space-y-4">
      <div class="glass-card !rounded-2xl p-4 relative overflow-hidden">
        <img :src="uploadedImage" alt="题目预览" class="w-full rounded-xl max-h-[350px] object-contain mx-auto" />
        <button
          class="absolute top-6 right-6 w-8 h-8 rounded-lg bg-black/40 flex items-center justify-center hover:bg-black/60 transition-colors"
          @click="uploadedImage = null"
        >
          <span class="text-white text-xs">x</span>
        </button>
      </div>

      <button
        :disabled="isProcessing"
        :class="[
          'w-full py-3.5 rounded-xl text-white font-semibold flex items-center justify-center gap-2 transition-all',
          isProcessing ? 'bg-purple-300 cursor-wait' : 'gradient-primary shadow-md shadow-purple-200 active:scale-[0.98]'
        ]"
        @click="startRecognition"
      >
        <component :is="isProcessing ? Sparkles : ImageIcon" :size="18" />
        {{ isProcessing ? '识别中...' : '开始识别，进入引导讲解' }}
      </button>

      <p class="text-xs text-center" style="color: var(--color-text-tertiary)">
        AI 将自动识别题目并开始苏格拉底式引导讲解
      </p>
    </div>
  </div>
</template>

<style scoped>
.upload-area {
  border: 2px dashed rgba(108, 92, 231, 0.25);
}
</style>
