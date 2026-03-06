# Faish - 基于 Faiss 的以图搜图工具

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Faish 是一个基于内容的图像检索（Content-Based Image Retrieval, CBIR）系统，使用 Facebook AI 团队开发的 [Faiss](https://faiss.ai/) 开源库实现高效的向量相似性搜索。

## 功能特性

- **图像特征提取**：使用 ResNet50 提取 2048 维图像特征向量
- **Faiss 索引**：支持 FlatL2（精确检索）和 IVF（近似检索）
- **相似图像检索**：基于内容的图像检索，返回 TOP-K 最相似结果
- **数据集管理**：支持文件夹/ZIP批量上传，实时显示上传进度
- **索引管理**：构建索引、清除索引，实时显示构建进度
- **桌面应用**：基于 Electron + Vue3 的跨平台桌面客户端
- **Web 界面**：基于 Vue3 + Vite 的现代化 Web 界面
- **批量处理**：使用 PyTorch DataLoader 实现高效的批量特征提取
- **动态参数**：根据数据集大小自动限制返回结果数量

## 技术栈

### 后端
- **Python 3.10+**
- **FastAPI**：高性能 Web 框架
- **PyTorch + TorchVision**：深度学习框架
- **Faiss**：向量相似性检索库
- **Pillow**：图像处理

### 前端
- **Vue 3**：渐进式 JavaScript 框架
- **Vite**：下一代前端构建工具
- **Electron**：跨平台桌面应用框架
- **Element Plus**：Vue 3 组件库
- **Pinia**：状态管理
- **Axios**：HTTP 客户端

## 项目结构

```
faish/
├── backend/
│   └── app.py              # FastAPI 后端服务
├── frontend/               # Vue3 + Electron 前端
│   ├── electron/
│   │   ├── main.cjs        # Electron 主进程
│   │   └── preload.cjs     # Electron 预加载脚本
│   ├── src/
│   │   ├── api/            # API 接口
│   │   ├── components/     # Vue 组件
│   │   │   ├── DatasetManager.vue    # 数据集管理组件
│   │   │   ├── ImageUploader.vue     # 图像上传组件
│   │   │   ├── SearchResults.vue     # 搜索结果组件
│   │   │   └── ImageCard.vue         # 图像卡片组件
│   │   ├── stores/         # Pinia 状态管理
│   │   │   ├── dataset.js  # 数据集状态
│   │   │   ├── search.js   # 搜索状态
│   │   │   └── health.js   # 服务健康状态
│   │   └── views/          # 页面视图
│   │       └── Home.vue    # 主页面
│   ├── package.json
│   └── vite.config.js
├── dataset_manager.py      # 数据集管理
├── faiss_index.py         # Faiss 索引管理
├── feature_extractor.py   # 特征提取
├── searcher.py            # 搜索主类
├── requirements.txt       # Python 依赖
├── README.md              # 项目说明
└── PROJECT_DESCRIPTION.md # 详细项目文档
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- Windows / macOS / Linux

### 1. 克隆项目

```bash
git clone <repository-url>
cd faish
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 启动服务

#### 方式一：Web 模式

```bash
# 终端 1：启动后端
python backend/app.py

# 终端 2：启动前端开发服务器
cd frontend
npm run dev
```

访问 http://localhost:5173

#### 方式二：桌面应用模式

```bash
# 启动后端
python backend/app.py

# 构建前端
cd frontend
npm run build

# 启动 Electron
npx electron .
```

## 使用说明

### Web 界面

1. **数据集管理**
   - 点击「选择图像文件」或「上传 ZIP 压缩包」上传图像
   - 在文件列表中可查看已选择的文件，点击 × 可删除单个文件
   - 点击「确认上传」将文件上传到数据集
   - 点击「构建索引」开始构建 Faiss 索引（显示实时进度）
   - 点击「清除索引」清空所有索引和数据集文件

2. **图像搜索**
   - 上传查询图像（拖拽或点击）
   - 调整返回数量滑块（自动限制为数据集大小）
   - 点击「开始搜索」获取相似结果
   - 点击「清除」清空搜索图像和结果

3. **状态显示**
   - 右上角显示服务状态和数据集统计
   - 构建索引时显示实时进度条
   - 搜索结果展示相似度百分比和距离

### 命令行工具

```bash
# 构建索引并搜索
python main.py --build --search --query test/query.jpg --topk 5

# 仅构建索引
python main.py --build

# 仅执行搜索
python main.py --search --query test/query.jpg --topk 5

# 使用 IVF 索引（大规模数据集）
python main.py --build --use_ivf
```

## API 文档

后端服务启动后，访问 http://localhost:8000/docs 查看完整的 API 文档（Swagger UI）。

### 主要接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/search | 图像相似性搜索 |
| POST | /api/dataset/upload | 上传图像文件 |
| POST | /api/dataset/upload-zip | 上传 ZIP 压缩包 |
| POST | /api/dataset/build | 构建 Faiss 索引 |
| POST | /api/dataset/clear | 清除索引和数据集 |
| GET | /api/dataset/status | 获取数据集状态 |
| GET | /api/image/{path} | 获取图像文件 |
| GET | /api/health | 服务健康检查 |

## 常见问题

### Q1: Faiss 安装失败？

```bash
# 使用 conda 安装
conda install -c pytorch faiss-cpu
```

### Q2: 出现 OpenMP 警告？

```bash
# Windows PowerShell
$env:KMP_DUPLICATE_LIB_OK="TRUE"

# CMD
set KMP_DUPLICATE_LIB_OK=TRUE
```

### Q3: Electron 启动白屏？

确保已执行 `npm run build` 生成 dist 目录。

### Q4: 端口被占用？

```bash
# Windows：查找并结束占用 8000 端口的进程
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
```

