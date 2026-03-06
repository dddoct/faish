<template>
  <div class="uploader">
    <el-upload
      class="upload-area"
      drag
      action="#"
      :auto-upload="false"
      :on-change="handleChange"
      :show-file-list="false"
      accept="image/*"
    >
      <el-icon class="upload-icon"><Upload /></el-icon>
      <div class="upload-text">
        <span class="primary">点击或拖拽图像到此处</span>
        <span class="secondary">支持 JPG、PNG、WEBP 格式</span>
      </div>
    </el-upload>
    
    <!-- 预览区域 -->
    <div v-if="previewUrl" class="preview-area">
      <el-image 
        :src="previewUrl" 
        fit="contain"
        class="preview-image"
      />
      <div class="preview-actions">
        <el-button 
          type="primary" 
          size="large"
          :loading="loading"
          @click="handleSearch"
        >
          <el-icon><Search /></el-icon>
          {{ loading ? '搜索中...' : '开始搜索' }}
        </el-button>
        <el-button 
          size="large"
          @click="handleClear"
        >
          <el-icon><Delete /></el-icon>
          清除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['upload', 'clear'])

const previewUrl = ref('')
const currentFile = ref(null)

const handleChange = (file) => {
  if (file.raw) {
    currentFile.value = file.raw
    previewUrl.value = URL.createObjectURL(file.raw)
  }
}

const handleSearch = () => {
  if (currentFile.value) {
    emit('upload', currentFile.value)
  }
}

const handleClear = () => {
  previewUrl.value = ''
  currentFile.value = null
  emit('clear')
}
</script>

<style scoped>
.uploader {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  height: 280px;
  background: rgba(255, 255, 255, 0.95);
  border: 2px dashed #dcdfe6;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.3s ease;
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: #409eff;
  background: rgba(255, 255, 255, 1);
}

.upload-icon {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 16px;
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-text .primary {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.upload-text .secondary {
  font-size: 14px;
  color: #909399;
}

.preview-area {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.preview-image {
  width: 100%;
  height: 300px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}
</style>
