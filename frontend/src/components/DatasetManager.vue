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
          <div class="section-header">
            <h4>上传图像</h4>
            <span class="section-tip">支持 JPG、PNG、WEBP 等格式，可多选文件或上传 ZIP 压缩包</span>
          </div>
          <div class="upload-row">
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
            
            <!-- el-upload文件列表放在单独一行 -->
            <div v-if="fileList.length > 0" class="el-upload-file-list">
              <div class="file-list-header">已选择 {{ fileList.length }} 个文件</div>
              <div class="file-list-content">
                <div 
                  v-for="file in fileList" 
                  :key="file.uid"
                  class="file-list-item"
                >
                  <el-icon class="file-icon"><Document /></el-icon>
                  <span class="file-name" :title="file.name">{{ file.name }}</span>
                  <el-icon class="file-delete" @click="handleFileRemove(file)"><Close /></el-icon>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 确认上传按钮 -->
          <div v-if="fileList.length > 0" class="upload-confirm-section">
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
        
        <!-- 分隔线 -->
        <el-divider class="section-divider" />
        
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
          
          <!-- 清除索引按钮 -->
          <el-button
            type="danger"
            size="large"
            :disabled="datasetStore.isBuilding || (datasetStore.indexedCount === 0 && datasetStore.datasetCount === 0)"
            @click="handleClear"
            class="clear-btn"
          >
            <el-icon><Delete /></el-icon>
            清除索引
          </el-button>
          
        </div>
        
        <!-- 提示文字 -->
        <p v-if="datasetStore.datasetCount === 0" class="build-tip">
          请先上传图像文件
        </p>
        
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
import { ElMessage, ElMessageBox } from 'element-plus'

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

const handleClear = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清除所有索引和数据集吗？此操作不可恢复！',
      '警告',
      {
        confirmButtonText: '确定清除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const result = await datasetStore.clearIndex()
    
    if (result.success) {
      ElMessage.success(result.message)
      buildJustFinished.value = false
    } else {
      ElMessage.error(result.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清除失败：' + error.message)
    }
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
  margin: 0;
  color: #333;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.section-tip {
  font-size: 12px;
  color: #909399;
}

.upload-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.upload-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: center;
}

.upload-btn {
  flex-shrink: 0;
}

.upload-btn :deep(.el-upload) {
  display: block;
}

/* 完全隐藏el-upload自带的文件列表 */
.upload-btn :deep(.el-upload-list) {
  display: none !important;
}

/* 自定义文件列表样式 */
.el-upload-file-list {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #f5f7fa;
  max-height: 200px;
  overflow-y: auto;
}

.el-upload-file-list .file-list-header {
  padding: 8px 12px;
  background-color: #e4e7ed;
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  border-bottom: 1px solid #dcdfe6;
}

.el-upload-file-list .file-list-content {
  padding: 4px 0;
}

.el-upload-file-list .file-list-item {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  gap: 8px;
  font-size: 13px;
  color: #606266;
}

.el-upload-file-list .file-list-item:hover {
  background-color: #e4e7ed;
}

.el-upload-file-list .file-icon {
  color: #909399;
  flex-shrink: 0;
}

.el-upload-file-list .file-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.el-upload-file-list .file-delete {
  color: #f56c6c;
  cursor: pointer;
  flex-shrink: 0;
}

.el-upload-file-list .file-delete:hover {
  color: #f78989;
}

.el-upload-file-list::-webkit-scrollbar {
  width: 6px;
}

.el-upload-file-list::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 3px;
}

.el-upload-file-list::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}

.upload-confirm-section {
  margin-top: 12px;
  display: flex;
  justify-content: center;
}

.upload-confirm-btn {
  width: auto;
  min-width: 140px;
  max-width: 200px;
  height: 36px;
  font-size: 13px;
}

.section-divider {
  margin: 8px 0;
}

.build-section {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.build-btn {
  min-width: 140px;
}

.clear-btn {
  min-width: 140px;
}

.build-tip {
  margin: 8px 0 0 0;
  font-size: 12px;
  color: #909399;
  text-align: center;
  width: 100%;
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
