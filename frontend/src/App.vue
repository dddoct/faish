<template>
  <div class="app">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <el-icon class="logo-icon"><Search /></el-icon>
          <h1 class="title">图像检索系统</h1>
          <div class="status">
            <!-- 始终显示服务正常 -->
            <div class="status-badge">
              <el-icon class="status-badge-icon"><CircleCheckFilled /></el-icon>
              <span class="status-badge-text">服务正常</span>
            </div>
          </div>
        </div>
      </el-header>
      
      <el-main class="main">
        <Home />
      </el-main>
      
      <el-footer class="footer">
        <p>
          基于 Faiss + ResNet50 的以图搜图系统
          <span v-if="datasetStore.indexedCount > 0">| 共 {{ datasetStore.indexedCount }} 张图像索引</span>
        </p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Home from './views/Home.vue'
import { useDatasetStore } from './stores/dataset'

const datasetStore = useDatasetStore()

onMounted(() => {
  // 定期刷新数据集状态
  datasetStore.fetchStatus()
  setInterval(() => {
    datasetStore.fetchStatus()
  }, 5000)
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-icon {
  font-size: 32px;
  color: #667eea;
  margin-right: 12px;
}

.title {
  flex: 1;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.status {
  display: flex;
  align-items: center;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #67c23a;
  border-radius: 4px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  height: 36px;
  box-sizing: border-box;
}

.status-badge-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.status-badge-text {
  white-space: nowrap;
  line-height: 1;
}

.main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
  width: 100%;
}

.footer {
  background: rgba(255, 255, 255, 0.9);
  text-align: center;
  color: #666;
  font-size: 14px;
}

.footer p {
  margin: 0;
  line-height: 60px;
}
</style>
