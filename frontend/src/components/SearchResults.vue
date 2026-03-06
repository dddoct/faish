<template>
  <div class="search-results">
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-icon><Collection /></el-icon>
            <span>搜索结果</span>
          </div>
          <div class="header-right">
            <el-tag type="info" effect="plain">
              耗时: {{ searchTime }}ms
            </el-tag>
            <el-tag type="success" effect="plain">
              共 {{ results.length }} 个结果
            </el-tag>
          </div>
        </div>
      </template>
      
      <div class="results-grid">
        <!-- 查询图像 -->
        <div class="result-item query-item">
          <div class="item-label">查询图像</div>
          <el-image 
            :src="getImageUrl(queryImage)" 
            fit="cover"
            class="result-image"
            :preview-src-list="[getImageUrl(queryImage)]"
          />
        </div>
        
        <!-- 搜索结果 -->
        <ImageCard 
          v-for="result in results" 
          :key="result.rank"
          :result="result"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import ImageCard from './ImageCard.vue'
import { searchApi } from '../api/search'

const props = defineProps({
  results: {
    type: Array,
    required: true
  },
  queryImage: {
    type: String,
    required: true
  },
  searchTime: {
    type: Number,
    default: 0
  }
})

const getImageUrl = (path) => {
  if (!path) return ''
  // 如果是本地临时文件路径，直接使用
  if (path.startsWith('temp/') || path.startsWith('temp\\')) {
    return searchApi.getImageUrl(path)
  }
  return searchApi.getImageUrl(path)
}
</script>

<style scoped>
.search-results {
  margin-top: 8px;
}

.results-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
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
  font-size: 18px;
  color: #333;
}

.header-right {
  display: flex;
  gap: 8px;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 8px;
}

.result-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.result-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.query-item {
  border: 3px solid #409eff;
}

.item-label {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.7), transparent);
  color: white;
  padding: 8px 12px;
  font-weight: 600;
  font-size: 14px;
  z-index: 1;
}

.query-item .item-label {
  background: linear-gradient(to bottom, #409eff, transparent);
}

.result-image {
  width: 100%;
  height: 200px;
  display: block;
}
</style>
