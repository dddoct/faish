import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const useHealthStore = defineStore('health', () => {
  const isReady = ref(false)
  const imageCount = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const checkHealth = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`${API_BASE_URL}/api/health`)
      isReady.value = response.data.index_loaded
      imageCount.value = response.data.image_count
    } catch (err) {
      isReady.value = false
      imageCount.value = 0
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  return {
    isReady,
    imageCount,
    loading,
    error,
    checkHealth
  }
})
