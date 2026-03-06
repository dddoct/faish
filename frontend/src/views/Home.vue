<template>
  <div class="home">
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
    
    <!-- 空状态 -->
    <el-empty 
      v-else-if="!searchStore.loading"
      description="上传图像开始搜索"
      :image-size="200"
    >
      <template #image>
        <el-icon class="empty-icon"><Picture /></el-icon>
      </template>
    </el-empty>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ImageUploader from '../components/ImageUploader.vue'
import SearchResults from '../components/SearchResults.vue'
import { useSearchStore } from '../stores/search'

const searchStore = useSearchStore()
const topk = ref(5)

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
</style>
