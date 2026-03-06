const { contextBridge } = require('electron')

// 可以在这里暴露安全的 API 给前端使用
contextBridge.exposeInMainWorld('electronAPI', {
  // 示例：暴露版本信息
  versions: {
    node: process.versions.node,
    electron: process.versions.electron
  }
})
