const { app, BrowserWindow, shell } = require('electron')
const path = require('path')
const { spawn } = require('child_process')

let mainWindow = null
let pythonProcess = null

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../public/icon.png'),
    show: false
  })

  // 开发模式：加载 Vite 开发服务器
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 打开外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })
}

// 启动后端服务
function startBackend() {
  const backendPath = path.join(__dirname, '..', 'backend', 'app.py')
  
  pythonProcess = spawn('python', [backendPath], {
    stdio: 'inherit',
    shell: true
  })

  pythonProcess.on('error', (err) => {
    console.error('Failed to start backend:', err)
  })

  pythonProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`)
  })

  console.log('Backend started on http://localhost:8000')
}

app.whenReady().then(() => {
  // 启动后端服务
  startBackend()
  
  // 创建主窗口
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  // 停止后端进程
  if (pythonProcess) {
    pythonProcess.kill()
  }
  
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  if (pythonProcess) {
    pythonProcess.kill()
  }
})
