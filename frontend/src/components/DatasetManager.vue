<template>
  <div class="dataset-manager">
    <el-card class="manager-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Folder /></el-icon>
            <span>数据集管理</span>
          </div>
          <el-tag :type="datasetStore.isBuilding ? 'warning' : (datasetStore.indexedCount > 0 ? 'success' : 'info')">
            {{ datasetStore.isBuilding ? '构建中...' : (datasetStore.indexedCount > 0 ? `已索引 ${datasetStore.indexedCount} 张` : '未索引') }}
          </el-tag>
        </div>
      </template>
      
      <div class="manager-content">
        <!-- 上传方式选择 -->
        <div class="upload-section">
          <h4>上传图像</h4>
          <div class="upload-options">
            <el-upload
              ref="imageUploadRef"
              class="upload-btn"
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileList"
              multiple
              accept=".jpg,.jpeg,.png,.bmp,.gif,.webp"
            >
              <el-button type="primary" size="large" :loading="isUploading">
                <el-icon><Picture /></el-icon>
                {{ isUploading ? `上传中 ${uploadProgress}%` : '选择图像文件' }}
              </el-button>
            </el-upload>
            
            <el-upload
              ref="zipUploadRef"
              class="upload-btn"
              action="#"
              :auto-upload="false"
              :on-change="handleZipChange"
              :show-file-list="false"
              accept=".zip"
            >
              <el-button type="info" size="large" :loading="isUnzipping">
                <el-icon><FolderOpened /></el-icon>
                {{ isUnzipping ? '解压中...' : '上传 ZIP 压缩包' }}
              </el-button>
            </el-upload>
          </div>
          <p class="upload-tip">支持 JPG、PNG、WEBP 等格式，可多选文件或上传 ZIP 压缩包</p>
          
          <!-- 已选文件列表 -->
          <div v-if="fileList.length > 0" class="file-list">
            <el-divider />
            <p class="file-list-title">已选择 {{ fileList.length }} 个文件</p>
            <el-scrollbar max-height="120">
              <div class="file-items">
                <el-tag 
                  v-for="file in fileList.slice(0, 10)" 
                  :key="file.uid"
                  closable
                  @close="handleFileRemove(file)"
                  class="file-tag"
                >
                  {{ file.name }}
                </el-tag>
                <el-tag v-if="fileList.length > 10">+{{ fileList.length - 10 }} 更多</el-tag>
              </div>
            </el-scrollbar>
            <el-button 
              type="success" 
              size="small" 
              @click="uploadSelectedFiles"
              :loading="isUploading"
              class="upload-confirm-btn"
            >
              <el-icon><Upload /></el-icon>
              确认上传 {{ fileList.length }} 个文件
            </el-button>
          </div>
        </div>
        
        <!-- 构建索引按钮 -->
        <div class="build-section">
          <el-button
            type="success"
            size="large"
            :loading="datasetStore.isBuilding"
            :disabled="datasetStore.datasetCount === 0 || datasetStore.isBuilding"
            @click="handleBuild"
            class="build-btn"
          >
            <el-icon><Refresh /></el-icon>
            {{ datasetStore.isBuilding ? '构建中...' : '构建索引' }}
          </el-button>
          
          <p v-if="datasetStore.datasetCount === 0" class="build-tip">
            请先上传图像文件
          </p>
        </div>
        
        <!-- 构建成功提示 -->
        <div v-if="!datasetStore.isBuilding && datasetStore.indexedCount > 0 && buildJustFinished" class="success-section">
          <el-result
            icon="success"
            title="索引构建完成"
            :sub-title="`共索引 ${datasetStore.indexedCount} 张图像，现在可以进行搜索了`"
          >
            <template #extra>
              <el-button type="primary" @click="scrollToSearch">
                <el-icon><Search /></el-icon>
                去搜索
              </el-button>
            </template>
          </el-result>
        </div>
        
        <!-- 进度显示 -->
        <div v-if="datasetStore.isBuilding" class="progress-section">
          <div class="progress-header">
            <el-icon class="progress-icon loading"><Loading /></el-icon>
            <span class="progress-title">正在构建索引</span>
            <el-tag size="small" type="warning">
              {{ datasetStore.buildProgress }} / {{ datasetStore.buildTotal }}
            </el-tag>
          </div>
          <el-progress 
            :percentage="buildPercentage"
            :status="buildStatus"
            :stroke-width="24"
            striped
            striped-flow
            :duration="10"
            class="build-progress"
          />
          <p class="progress-message">{{ datasetStore.buildMessage }}</p>
          <div class="progress-stats">
            <el-statistic title="已处理" :value="datasetStore.buildProgress" />
            <el-statistic title="总计" :value="datasetStore.buildTotal" />
            <el-statistic title="进度" :value="buildPercentage" suffix="%" />
          </div>
        </div>
        
        <!-- 统计信息 -->
        <div class="stats-section">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="数据集中图像">
              <el-tag size="small" type="info">{{ datasetStore.datasetCount }} 张</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="已建立索引">
              <el-tag size="small" :type="datasetStore.indexedCount > 0 ? 'success' : 'info'">
                {{ datasetStore.indexedCount }} 张
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item v-if="datasetStore.lastBuildTime" label="上次构建时间">
              {{ datasetStore.lastBuildTime }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useDatasetStore } from '../stores/dataset'
import { ElMessage } from 'element-plus'

const datasetStore = useDatasetStore()
const fileList = ref([])
const isUploading = ref(false)
const isUnzipping = ref(false)
const uploadProgress = ref(0)
const imageUploadRef = ref(null)
const zipUploadRef = ref(null)
const buildJustFinished = ref(false)

const buildPercentage = computed(() => {
  if (datasetStore.buildTotal === 0) return 0
  return Math.round((datasetStore.buildProgress / datasetStore.buildTotal) * 100)
})

const buildStatus = computed(() => {
  if (buildPercentage.value === 100) return 'success'
  return ''
})

// 监听构建状态变化
watch(() => datasetStore.isBuilding, (newVal, oldVal) => {
  // 从构建中变为非构建中，且索引数量大于0，表示构建完成
  if (oldVal === true && newVal === false && datasetStore.indexedCount > 0) {
    buildJustFinished.value = true
    ElMessage.success(`索引构建完成！共 ${datasetStore.indexedCount} 张图像`)
    // 5秒后自动隐藏成功提示
    setTimeout(() => {
      buildJustFinished.value = false
    }, 5000)
  }
})

const scrollToSearch = () => {
  // 滚动到搜索区域
  window.scrollTo({ top: 400, behavior: 'smooth' })
}

const handleFileChange = (file) => {
  // 添加到文件列表，但不立即上传
  const exists = fileList.value.some(f => f.name === file.name)
  if (!exists) {
    fileList.value.push(file)
  }
}

const handleFileRemove = (file) => {
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const uploadSelectedFiles = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  isUploading.value = true
  uploadProgress.value = 0
  
  try {
    // 模拟进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 15
      }
    }, 200)
    
    const files = fileList.value.map(f => f.raw)
    const result = await datasetStore.uploadFiles(files)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    if (result.success) {
      ElMessage.success(result.message)
      fileList.value = [] // 清空列表
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    setTimeout(() => {
      isUploading.value = false
      uploadProgress.value = 0
    }, 500)
  }
}

const handleZipChange = async (file) => {
  if (!file.raw) return
  
  isUnzipping.value = true
  
  try {
    const result = await datasetStore.uploadZip(file.raw)
    
    if (result.success) {
      ElMessage.success(result.message)
      // 清空上传组件
      if (zipUploadRef.value) {
        zipUploadRef.value.clearFiles()
      }
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    ElMessage.error('上传失败')
  } finally {
    isUnzipping.value = false
  }
}

const handleBuild = async () => {
  const result = await datasetStore.buildIndex()
  
  if (result.success) {
    ElMessage.success('开始构建索引')
    // 开始轮询进度
    datasetStore.startPolling()
  } else {
    ElMessage.error(result.message)
  }
}
</script>

<style scoped>
.dataset-manager {
  margin-bottom: 24px;
}

.manager-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.manager-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-section h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.upload-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.upload-btn :deep(.el-upload) {
  display: block;
}

.upload-tip {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.file-list {
  margin-top: 12px;
}

.file-list-title {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.file-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px 0;
}

.file-tag {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.upload-confirm-btn {
  margin-top: 12px;
}

.build-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.build-btn {
  width: 200px;
}

.build-tip {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.success-section {
  padding: 20px;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  border-radius: 12px;
  border: 2px solid #67c23a;
  margin-bottom: 16px;
}

.success-section :deep(.el-result__icon) {
  font-size: 64px;
  color: #67c23a;
}

.progress-section {
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 12px;
  border: 1px solid #e6e6e6;
}

.progress-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.progress-icon {
  font-size: 24px;
  color: #e6a23c;
}

.progress-icon.loading {
  animation: rotate 1.5s linear infinite;
}

.progress-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.build-progress {
  margin-bottom: 12px;
}

.progress-message {
  margin: 0 0 16px 0;
  text-align: center;
  color: #606266;
  font-size: 14px;
  font-weight: 500;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  gap: 16px;
}

.progress-stats :deep(.el-statistic__content) {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.progress-stats :deep(.el-statistic__title) {
  font-size: 12px;
  color: #909399;
}

.stats-section {
  margin-top: 8px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
