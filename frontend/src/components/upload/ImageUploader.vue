<script setup lang="ts">
/**
 * ImageUploader - 通用图片上传组件
 * 支持点击上传、拖拽上传、拍照、图片预览和删除
 */
import { ref } from 'vue'
import { Camera, Upload, X, ImageIcon } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  /** 已上传的图片 URL (dataURL 或 URL) */
  modelValue?: string | null
  /** 是否正在处理 */
  loading?: boolean
  /** 提示文字 */
  hint?: string
  /** 最大文件大小 (MB) */
  maxSize?: number
}>(), {
  modelValue: null,
  loading: false,
  hint: '支持 JPG、PNG 格式，可拖拽图片到此处上传',
  maxSize: 10,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | null]
  'select': [file: File]
}>()

const isDragging = ref(false)
const fileInputRef = ref<HTMLInputElement>()

function handleFileSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files?.[0]) {
    validateAndPreview(input.files[0])
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  event.preventDefault()
  const file = event.dataTransfer?.files?.[0]
  if (file) {
    validateAndPreview(file)
  }
}

function validateAndPreview(file: File) {
  // 校验类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }
  // 校验大小
  if (file.size > props.maxSize * 1024 * 1024) {
    alert(`图片大小不能超过 ${props.maxSize}MB`)
    return
  }
  // 预览
  const reader = new FileReader()
  reader.onload = (e) => {
    const dataUrl = e.target?.result as string
    emit('update:modelValue', dataUrl)
    emit('select', file)
  }
  reader.readAsDataURL(file)
}

function removeImage() {
  emit('update:modelValue', null)
  // 重置 input 以便重新选择同一文件
  if (fileInputRef.value) fileInputRef.value.value = ''
}
</script>

<template>
  <div class="image-uploader">
    <!-- 上传区域 -->
    <div
      v-if="!modelValue"
      :class="[
        'upload-zone',
        isDragging && 'is-dragging',
      ]"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="(fileInputRef as HTMLInputElement)?.click()"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleFileSelect"
      />

      <div class="upload-icon-wrap">
        <Camera :size="32" class="text-purple-500" />
      </div>

      <p class="upload-title">点击或拖拽上传</p>
      <p class="upload-hint">{{ hint }}</p>

      <div class="upload-actions">
        <button class="btn-primary" @click.stop="(fileInputRef as HTMLInputElement)?.click()">
          <Camera :size="14" />
          拍照
        </button>
        <button class="btn-secondary" @click.stop="(fileInputRef as HTMLInputElement)?.click()">
          <Upload :size="14" />
          选择图片
        </button>
      </div>
    </div>

    <!-- 图片预览区 -->
    <div v-else class="preview-container">
      <img :src="modelValue" alt="预览图" class="preview-image" />
      <button
        v-if="!loading"
        class="remove-btn"
        title="移除图片"
        @click="removeImage"
      >
        <X :size="14" />
      </button>
      <div v-if="loading" class="loading-overlay">
        <div class="spinner" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.image-uploader { width: 100%; }

.upload-zone {
  border: 2px dashed rgba(108, 92, 231, 0.25);
  border-radius: 1rem;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  min-height: 280px;
  transition: all 0.2s ease;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(8px);
}
.upload-zone:hover,
.upload-zone.is-dragging {
  border-color: rgba(108, 92, 231, 0.6);
  background: rgba(108, 92, 231, 0.04);
}

.upload-icon-wrap {
  width: 4rem;
  height: 4rem;
  border-radius: 50%;
  background: rgba(108, 92, 231, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
}

.upload-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 0.25rem;
}

.upload-hint {
  font-size: 0.85rem;
  color: var(--color-text-tertiary);
  text-align: center;
  max-width: 16rem;
  line-height: 1.5;
}

.upload-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 1.15rem;
  border-radius: 0.75rem;
  background: linear-gradient(135deg, #6c5ce7, #a855f7);
  color: white;
  font-size: 0.85rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(108, 92, 231, 0.25);
  transition: transform 0.15s;
}
.btn-primary:active { transform: scale(0.97); }

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 1.15rem;
  border-radius: 0.75rem;
  border: 1px solid #e5e7eb;
  background: white;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-secondary:hover { background: #f9fafb; }

.preview-container {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(8px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.preview-image {
  width: 100%;
  max-height: 350px;
  object-fit: contain;
  display: block;
}

.remove-btn {
  position: absolute;
  top: 0.65rem;
  right: 0.65rem;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(4px);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.15s;
}
.remove-btn:hover { opacity: 1; }

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #e5e7eb;
  border-top-color: #6c5ce7;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
