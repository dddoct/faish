import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

export const searchApi = {
  /**
   * 上传图像进行搜索
   * @param {File} imageFile - 图像文件
   * @param {number} topk - 返回结果数量
   * @returns {Promise}
   */
  search(imageFile, topk = 5) {
    const formData = new FormData()
    formData.append('image', imageFile)
    formData.append('topk', topk)
    
    return api.post('/api/search', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 获取图像 URL
   * @param {string} path - 图像路径
   * @returns {string}
   */
  getImageUrl(path) {
    // 将路径中的 / 替换为 ___
    const encodedPath = path.replace(/\//g, '___')
    return `${API_BASE_URL}/api/image/${encodedPath}`
  },

  /**
   * 健康检查
   * @returns {Promise}
   */
  health() {
    return api.get('/api/health')
  }
}

export default api
