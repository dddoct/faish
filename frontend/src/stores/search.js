import { defineStore } from 'pinia'
import { ref } from 'vue'
import { searchApi } from '../api/search'
import { ElMessage } from 'element-plus'

export const useSearchStore = defineStore('search', () => {
  const results = ref([])
  const queryImage = ref('')
  const searchTime = ref(0)
  const loading = ref(false)
  const error = ref(null)

  const search = async (file, topk = 5) => {
    loading.value = true
    error.value = null
    results.value = []
    
    try {
      const response = await searchApi.search(file, topk)
      
      if (response.data.success) {
        results.value = response.data.data.results
        queryImage.value = response.data.data.query_image
        searchTime.value = response.data.data.time_ms
        
        ElMessage.success(`搜索完成，找到 ${results.value.length} 个相似图像`)
      } else {
        throw new Error('搜索失败')
      }
    } catch (err) {
      error.value = err.message
      results.value = []
      ElMessage.error(`搜索失败: ${err.response?.data?.detail || err.message}`)
    } finally {
      loading.value = false
    }
  }

  const clearResults = () => {
    results.value = []
    queryImage.value = ''
    searchTime.value = 0
    error.value = null
  }

  return {
    results,
    queryImage,
    searchTime,
    loading,
    error,
    search,
    clearResults
  }
})
