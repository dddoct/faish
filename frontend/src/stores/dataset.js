import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const useDatasetStore = defineStore('dataset', () => {
  const indexedCount = ref(0)
  const datasetCount = ref(0)
  const isBuilding = ref(false)
  const buildProgress = ref(0)
  const buildTotal = ref(0)
  const buildMessage = ref('')
  const lastBuildTime = ref(null)
  let pollingInterval = null

  // 获取数据集状态
  const fetchStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/dataset/status`)
      const data = response.data
      
      indexedCount.value = data.indexed_count
      datasetCount.value = data.dataset_count
      isBuilding.value = data.is_building
      buildProgress.value = data.build_progress
      buildTotal.value = data.build_total
      buildMessage.value = data.build_message
      lastBuildTime.value = data.last_build_time
      
      // 如果构建完成，停止轮询
      if (!data.is_building && pollingInterval) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
      
      return data
    } catch (error) {
      console.error('获取数据集状态失败:', error)
      return null
    }
  }

  // 上传文件
  const uploadFiles = async (files) => {
    const formData = new FormData()
    files.forEach(file => {
      formData.append('files', file)
    })

    try {
      const response = await axios.post(`${API_BASE_URL}/api/dataset/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // 上传成功后刷新状态
      await fetchStatus()
      
      return {
        success: true,
        message: response.data.message,
        uploaded: response.data.uploaded
      }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '上传失败'
      }
    }
  }

  // 上传 ZIP
  const uploadZip = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/dataset/upload-zip`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      // 上传成功后刷新状态
      await fetchStatus()
      
      return {
        success: true,
        message: response.data.message,
        uploaded: response.data.uploaded
      }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '上传失败'
      }
    }
  }

  // 构建索引
  const buildIndex = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/dataset/build`)
      
      return {
        success: true,
        message: response.data.message
      }
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.detail || '构建失败'
      }
    }
  }

  // 开始轮询构建进度 - 持续轮询直到构建完成
  const startPolling = () => {
    // 清除之前的轮询
    if (pollingInterval) {
      clearInterval(pollingInterval)
    }
    
    // 立即获取一次状态
    fetchStatus()
    
    // 每1秒轮询一次，持续直到构建完成
    pollingInterval = setInterval(async () => {
      const data = await fetchStatus()
      // 如果构建完成或出错，停止轮询
      if (data && !data.is_building) {
        clearInterval(pollingInterval)
        pollingInterval = null
      }
    }, 1000)
  }

  // 停止轮询
  const stopPolling = () => {
    if (pollingInterval) {
      clearInterval(pollingInterval)
      pollingInterval = null
    }
  }

  return {
    indexedCount,
    datasetCount,
    isBuilding,
    buildProgress,
    buildTotal,
    buildMessage,
    lastBuildTime,
    fetchStatus,
    uploadFiles,
    uploadZip,
    buildIndex,
    startPolling,
    stopPolling
  }
})
