# 基于 Faiss 的以图搜图工具

## 项目简介

本项目基于 Facebook AI 团队开发的 [Faiss](https://faiss.ai/) 开源库，实现了一个高效的以图搜图（Content-Based Image Retrieval, CBIR）工具。使用预训练的深度学习模型（ResNet50）提取图像特征向量，通过 Faiss 进行快速的向量相似性检索。

## 核心功能

- **图像特征提取**：使用 ResNet50 模型提取 2048 维图像特征向量
- **Faiss 索引构建**：支持 FlatL2（精确检索）和 IVF（近似检索）两种索引类型
- **相似图像检索**：基于内容的图像检索，返回 TOP-K 最相似结果
- **结果可视化**：展示查询图像和检索结果的对比图
- **批量处理优化**：使用 PyTorch DataLoader 实现真正的批量特征提取

## 技术栈

- **Python 3.12**
- **PyTorch + TorchVision**：深度学习框架，用于图像特征提取
- **Faiss**：Facebook 开源的向量相似性检索库
- **PIL (Pillow)**：图像处理
- **Matplotlib**：结果可视化
- **NumPy**：数值计算

## 项目结构

```
faish/
├── main.py                    # 主程序入口
├── feature_extractor.py       # 图像特征提取模块
├── dataset_manager.py         # 数据集管理模块
├── faiss_index.py            # Faiss索引管理模块
├── searcher.py               # 搜索主类（整合模块）
├── check_deps.py             # 依赖检查脚本
├── requirements.txt          # 项目依赖
├── README.md                 # 项目说明文档
├── 实验题目.md                # 实验要求
├── 实验运行步骤.md            # 详细运行步骤
├── data/images/              # 图像数据集目录
├── index/                    # Faiss索引文件存储
└── test/                     # 查询图像目录
```

## 模块说明

### 1. feature_extractor.py
**图像特征提取模块**
- 使用预训练的 ResNet50 模型
- 提取 2048 维特征向量
- 支持单张和批量图像处理（使用 DataLoader）
- 对特征进行 L2 归一化

**核心类**：
- `_ImageDataset`: PyTorch Dataset 类，支持批量图像加载
- `ImageFeatureExtractor`: 特征提取器，支持 GPU 加速

### 2. dataset_manager.py
**数据集管理模块**
- 扫描指定目录下的图像文件
- 支持 jpg、jpeg、png、bmp、gif、webp 格式
- 管理图像路径列表

### 3. faiss_index.py
**Faiss索引管理模块**
- 构建向量索引（IndexFlatL2 / IndexIVFFlat）
- 自动创建索引目录（如果不存在）
- 保存和加载索引文件
- 执行相似性搜索

### 4. searcher.py
**搜索主类模块**
- 整合特征提取、数据集管理和索引模块
- 提供完整的图像搜索流程
- 支持结果可视化展示
- 无 GUI 环境自动降级处理（保存图片而非显示）

### 5. main.py
**主程序入口**
- 解析命令行参数
- 调用各模块完成构建索引和搜索任务

## 快速开始

### 1. 环境准备

确保已安装 Python 3.10+，然后安装依赖：

```bash
# 方式一：使用 pip
pip install -r requirements.txt

# 方式二：手动安装
pip install faiss-cpu>=1.7.4 torch>=2.0.0 torchvision>=0.15.0 Pillow>=9.0.0 numpy>=1.23.0 matplotlib>=3.6.0
```

### 2. 验证安装

```bash
python check_deps.py
```

### 3. 准备数据

- 将待检索的图像放入 `data/images/` 目录
- 将查询图像放入 `test/` 目录

### 4. 运行程序

```bash
# 构建索引并搜索
python main.py --build --search --query test/query_image.jpg --topk 5

# 仅构建索引
python main.py --build

# 仅执行搜索（需已有索引）
python main.py --search --query test/query_image.jpg --topk 5

# 保存搜索结果图（无GUI环境推荐）
python main.py --search --query test/query_image.jpg --save_result result.png

# 使用IVF索引（大规模数据集）
python main.py --build --use_ivf
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--build` | 构建索引 | - |
| `--search` | 执行搜索 | - |
| `--data_dir` | 图像数据集目录 | data/images |
| `--index_path` | 索引文件路径 | index/image_index.faiss |
| `--paths_path` | 图像路径文件 | index/image_paths.pkl |
| `--query` | 查询图像路径 | - |
| `--topk` | 返回结果数量 | 5 |
| `--use_ivf` | 使用IVF索引（大规模数据集） | False |
| `--save_result` | 保存结果图像路径 | - |

## 核心算法说明

### 图像特征提取流程

```
输入图像 (H×W×3)
    ↓
Resize to 224×224
    ↓
归一化 (ImageNet mean/std)
    ↓
ResNet50 前向传播
    ↓
全局平均池化
    ↓
输出特征向量 (2048维)
    ↓
L2 归一化
    ↓
归一化特征向量 (长度为1)
```

### 相似度计算

由于特征向量已进行 L2 归一化，欧氏距离与余弦相似度存在以下关系：

**L2 距离**：$$d = \sqrt{\sum_{i=1}^{n}(x_i - y_i)^2}$$

**余弦相似度**：$$cos(\theta) = 1 - \frac{d^2}{2}$$

**简化计算**（当 d 较小时）：$$similarity \approx 1 - \frac{d}{2}$$

本项目使用：`similarity = 1 - distance / 2`

- 距离越小 → 相似度越接近 1
- 距离越大 → 相似度越接近 0

### Faiss 索引类型

| 索引类型 | 适用场景 | 检索精度 | 内存占用 | 构建速度 |
|----------|----------|----------|----------|----------|
| IndexFlatL2 | < 10万张 | 100%精确 | 高 | 快 |
| IndexIVFFlat | > 10万张 | 近似 | 中 | 需训练 |

## 示例输出

```
==================================================
开始构建索引...
==================================================
找到 13 张图像
正在提取 13 张图像的特征...
进度: 0/13
进度: 10/13
构建索引，向量维度: 2048, 向量数量: 13
索引构建完成，包含 13 个向量
索引已保存到 index/image_index.faiss
==================================================
索引构建完成！
==================================================

==================================================
搜索图像: test/query.jpg
==================================================

搜索结果:
Rank 1: data/images\image1.jpg
  距离: 0.2635, 相似度: 0.8683
Rank 2: data/images\image2.jpg
  距离: 0.5558, 相似度: 0.7221
Rank 3: data/images\image3.jpg
  距离: 0.8349, 相似度: 0.5826
```

## 实验检查清单

- [x] 环境准备完成（依赖安装成功）
- [x] 项目目录结构创建完成
- [x] 图像数据集准备完成
- [x] feature_extractor.py 模块实现完成（含批量处理）
- [x] dataset_manager.py 模块实现完成（支持 webp）
- [x] faiss_index.py 模块实现完成（自动创建目录）
- [x] searcher.py 模块实现完成（正确相似度公式）
- [x] main.py 主程序实现完成
- [x] requirements.txt 创建完成
- [x] Faiss 索引构建成功
- [x] 图像检索功能正常
- [x] TOP-K 结果展示正确
- [x] 无 GUI 环境兼容处理

## 常见问题

### Q1: Faiss 安装失败？
尝试使用 conda 安装：
```bash
conda install -c pytorch faiss-cpu
```

### Q2: 出现 OpenMP 警告？
这是 PyTorch 和 NumPy 的兼容性问题。项目已在代码中自动设置环境变量解决此问题：
```python
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
```

如果仍然出现警告，可以手动设置：
```bash
# Windows PowerShell
$env:KMP_DUPLICATE_LIB_OK="TRUE"
python main.py --search --query test/query.jpg

# 或者使用 CMD
set KMP_DUPLICATE_LIB_OK=TRUE
python main.py --search --query test/query.jpg
```

### Q3: 检索结果不准确？
- 检查图像预处理是否正确
- 确认使用同一模型提取特征
- 尝试调整 TOP-K 参数

### Q4: 内存不足？
对于大规模数据集，使用 `--use_ivf` 参数启用 IVF 索引。

### Q5: 无 GUI 环境如何查看结果？
使用 `--save_result` 参数保存结果图像：
```bash
python main.py --search --query test/query.jpg --save_result result.png
```

### Q6: 支持哪些图像格式？
支持：jpg、jpeg、png、bmp、gif、webp

## 扩展功能（可选）

1. **Web 界面**：使用 Flask 或 Streamlit 构建可视化界面
2. **批量检索**：支持批量查询多张图像
3. **增量更新**：支持动态添加/删除图像
4. **GPU 加速**：使用 `faiss-gpu` 提升检索速度

## 参考资源

- Faiss 官方文档：https://faiss.ai/
- PyTorch 官方文档：https://pytorch.org/docs/
- ResNet 论文：https://arxiv.org/abs/1512.03385

## 更新日志

### v1.0 (2026-03-06)
- 初始版本发布
- 实现基于 ResNet50 + Faiss 的以图搜图功能
- 支持批量特征提取（DataLoader）
- 支持多种图像格式（含 webp）
- 优化相似度计算公式
- 兼容无 GUI 环境
- 修复 OpenMP 冲突问题（自动设置环境变量）
