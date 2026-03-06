<template>
  <div class="home">
    <!-- 数据集管理 -->
    <DatasetManager />
    
    <!-- 搜索区域 -->
    <template v-if="datasetStore.indexedCount > 0">
      <!-- 上传区域 -->
      <ImageUploader 
        @upload="handleUpload" 
        :loading="searchStore.loading"
      />
      
      <!-- 参数设置 -->
      <div class="settings">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>搜索参数</span>
            </div>
          </template>
          <div class="settings-content">
            <div class="setting-item">
              <span class="label">返回数量:</span>
              <el-slider v-model="topk" :min="1" :max="20" :step="1" show-stops style="width: 200px;" />
              <el-tag type="primary">{{ topk }} 张</el-tag>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 搜索结果 -->
      <SearchResults 
        v-if="searchStore.results.length > 0"
        :results="searchStore.results"
        :query-image="searchStore.queryImage"
        :search-time="searchStore.searchTime"
      />
    </template>
    
    <!-- 提示先构建索引 -->
    <el-empty 
      v-else-if="!datasetStore.isBuilding && datasetStore.datasetCount === 0"
      description="请先上传图像并构建索引"
      :image-size="200"
    >
      <template #image>
        <el-icon class="empty-icon"><FolderAdd /></el-icon>
      </template>
    </el-empty>
    
    <!-- 提示正在构建 -->
    <el-empty 
      v-else-if="datasetStore.isBuilding"
      description="正在构建索引，请稍候..."
      :image-size="200"
    >
      <template #image>
        <el-icon class="empty-icon loading"><Loading /></el-icon>
      </template>
    </el-empty>
    
    <!-- 提示构建索引 -->
    <el-empty 
      v-else
      description="请点击上方「构建索引」按钮"
      :image-size="200"
    >
      <template #image>
        <el-icon class="empty-icon"><Refresh /></el-icon>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import DatasetManager from '../components/DatasetManager.vue'
import ImageUploader from '../components/ImageUploader.vue'
import SearchResults from '../components/SearchResults.vue'
import { useSearchStore } from '../stores/search'
import { useDatasetStore } from '../stores/dataset'

const searchStore = useSearchStore()
const datasetStore = useDatasetStore()
const topk = ref(5)

onMounted(() => {
  // 获取数据集状态
  datasetStore.fetchStatus()
})

const handleUpload = async (file) => {
  await searchStore.search(file, topk.value)
}
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings {
  margin-top: 8px;
}

.settings-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
}

.settings-content {
  padding: 8px 0;
}

.setting-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.label {
  font-weight: 500;
  color: #666;
  min-width: 80px;
}

.empty-icon {
  font-size: 120px;
  color: #dcdfe6;
}

.empty-icon.loading {
  animation: rotate 2s linear infinite;
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
