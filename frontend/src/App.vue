<template>
  <div class="app">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <el-icon class="logo-icon"><Search /></el-icon>
          <h1 class="title">图像检索系统</h1>
          <div class="status">
            <el-tag v-if="healthStore.isReady" type="success" effect="dark">
              <el-icon><Check /></el-icon>
              服务正常
            </el-tag>
            <el-tag v-else type="danger" effect="dark">
              <el-icon><Close /></el-icon>
              服务异常
            </el-tag>
          </div>
        </div>
      </el-header>
      
      <el-main class="main">
        <Home />
      </el-main>
      
      <el-footer class="footer">
        <p>基于 Faiss + ResNet50 的以图搜图系统 | 共 {{ healthStore.imageCount }} 张图像索引</p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Home from './views/Home.vue'
import { useHealthStore } from './stores/health'

const healthStore = useHealthStore()

onMounted(() => {
  healthStore.checkHealth()
  // 每 10 秒检查一次服务状态
  setInterval(() => {
    healthStore.checkHealth()
  }, 10000)
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
  gap: 8px;
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
