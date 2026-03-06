<template>
  <div class="image-card">
    <div class="rank-badge">#{{ result.rank }}</div>
    <el-image 
      :src="imageUrl" 
      fit="cover"
      class="card-image"
      :preview-src-list="[imageUrl]"
    />
    <div class="card-info">
      <div class="similarity">
        <el-progress 
          :percentage="Math.round(result.similarity * 100)" 
          :color="getProgressColor"
          :stroke-width="8"
          :show-text="false"
        />
        <span class="similarity-text">{{ (result.similarity * 100).toFixed(1) }}%</span>
      </div>
      <div class="details">
        <el-tooltip :content="result.path" placement="bottom">
          <span class="path">{{ getFileName(result.path) }}</span>
        </el-tooltip>
        <span class="distance">距离: {{ result.distance.toFixed(4) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { searchApi } from '../api/search'

const props = defineProps({
  result: {
    type: Object,
    required: true
  }
})

const imageUrl = computed(() => {
  return searchApi.getImageUrl(props.result.path)
})

const getProgressColor = computed(() => {
  const similarity = props.result.similarity
  if (similarity >= 0.7) return '#67c23a'  // 绿色
  if (similarity >= 0.5) return '#e6a23c'  // 橙色
  return '#f56c6c'  // 红色
})

const getFileName = (path) => {
  if (!path) return ''
  const parts = path.split(/[\\/]/)
  return parts[parts.length - 1]
}
</script>

<style scoped>
.image-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background: white;
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.rank-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  z-index: 1;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.card-image {
  width: 100%;
  height: 160px;
  display: block;
}

.card-info {
  padding: 12px;
}

.similarity {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.similarity :deep(.el-progress) {
  flex: 1;
}

.similarity-text {
  font-weight: 600;
  font-size: 14px;
  color: #333;
  min-width: 50px;
  text-align: right;
}

.details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.path {
  font-size: 12px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.distance {
  font-size: 11px;
  color: #909399;
}
</style>
