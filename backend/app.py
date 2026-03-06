"""
FastAPI 后端服务
提供图像搜索 API 和数据集管理
"""
import os
import sys
import time
import shutil
import zipfile
import tempfile
from pathlib import Path
from typing import List, Optional
import asyncio

# 解决 OpenMP 冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 添加父目录到路径以导入 searcher
sys.path.insert(0, str(Path(__file__).parent.parent))
from searcher import ImageSearcher
from dataset_manager import ImageDatasetManager
from feature_extractor import ImageFeatureExtractor
from faiss_index import FaissIndexManager

# 创建 FastAPI 应用
app = FastAPI(
    title="图像检索系统 API",
    description="基于 Faiss 的以图搜图后端服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
searcher = None
INDEX_PATH = Path(__file__).parent.parent / "index" / "image_index.faiss"
PATHS_PATH = Path(__file__).parent.parent / "index" / "image_paths.pkl"
TEMP_DIR = Path(__file__).parent.parent / "temp"
DATASET_DIR = Path(__file__).parent.parent / "data" / "images"

# 确保目录存在
TEMP_DIR.mkdir(exist_ok=True)
DATASET_DIR.mkdir(parents=True, exist_ok=True)

# 构建状态
build_status = {
    "is_building": False,
    "progress": 0,
    "total": 0,
    "message": "",
    "last_build_time": None
}


def load_index():
    """加载索引"""
    global searcher
    try:
        searcher = ImageSearcher()
        if INDEX_PATH.exists() and PATHS_PATH.exists():
            searcher.load_index(str(INDEX_PATH), str(PATHS_PATH))
            print(f"✅ 索引加载成功，包含 {searcher.index_manager.index.ntotal} 个向量")
            return True
        else:
            print("⚠️ 索引文件不存在，请先构建索引")
            return False
    except Exception as e:
        print(f"❌ 索引加载失败: {e}")
        searcher = None
        return False


@app.on_event("startup")
async def startup_event():
    """启动时加载索引"""
    load_index()


@app.get("/api/health")
async def health_check():
    """健康检查接口 - 始终返回正常"""
    image_count = 0
    if searcher is not None and searcher.index_manager is not None and searcher.index_manager.index is not None:
        image_count = searcher.index_manager.index.ntotal
    
    return {
        "status": "ok",
        "index_loaded": image_count > 0,
        "image_count": image_count,
        "dataset_dir": str(DATASET_DIR)
    }


@app.get("/api/dataset/status")
async def dataset_status():
    """获取数据集状态"""
    image_count = 0
    if searcher is not None and searcher.index_manager is not None and searcher.index_manager.index is not None:
        image_count = searcher.index_manager.index.ntotal
    
    # 统计数据集目录中的图像数量
    dataset_images = 0
    if DATASET_DIR.exists():
        for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            dataset_images += len(list(DATASET_DIR.glob(f'*{ext}')))
            dataset_images += len(list(DATASET_DIR.glob(f'*{ext.upper()}')))
    
    return {
        "indexed_count": image_count,
        "dataset_count": dataset_images,
        "is_building": build_status["is_building"],
        "build_progress": build_status["progress"],
        "build_total": build_status["total"],
        "build_message": build_status["message"],
        "last_build_time": build_status["last_build_time"]
    }


@app.post("/api/dataset/upload")
async def upload_dataset(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """
    上传图像文件到数据集
    
    - **files**: 图像文件列表（支持多选）
    """
    if build_status["is_building"]:
        raise HTTPException(status_code=400, detail="正在构建索引，请稍后再上传")
    
    uploaded_count = 0
    errors = []
    
    for file in files:
        try:
            # 检查文件类型
            ext = Path(file.filename).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                errors.append(f"{file.filename}: 不支持的文件格式")
                continue
            
            # 保存文件
            target_path = DATASET_DIR / file.filename
            with open(target_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            uploaded_count += 1
            
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
        finally:
            file.file.close()
    
    return {
        "success": True,
        "uploaded": uploaded_count,
        "errors": errors,
        "message": f"成功上传 {uploaded_count} 个文件"
    }


@app.post("/api/dataset/upload-zip")
async def upload_dataset_zip(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    上传 ZIP 压缩包到数据集
    
    - **file**: ZIP 文件
    """
    if build_status["is_building"]:
        raise HTTPException(status_code=400, detail="正在构建索引，请稍后再上传")
    
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="只支持 ZIP 格式")
    
    uploaded_count = 0
    errors = []
    
    try:
        # 保存 ZIP 文件到临时目录
        temp_zip = TEMP_DIR / f"dataset_{int(time.time())}.zip"
        with open(temp_zip, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 解压 ZIP
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            for zip_info in zip_ref.infolist():
                # 检查文件类型
                ext = Path(zip_info.filename).suffix.lower()
                if ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
                    continue
                
                # 解压文件
                zip_info.filename = Path(zip_info.filename).name
                zip_ref.extract(zip_info, DATASET_DIR)
                uploaded_count += 1
        
        # 删除临时 ZIP 文件
        temp_zip.unlink()
        
    except Exception as e:
        errors.append(str(e))
    finally:
        file.file.close()
    
    return {
        "success": True,
        "uploaded": uploaded_count,
        "errors": errors,
        "message": f"成功解压 {uploaded_count} 个图像文件"
    }


async def build_index_async():
    """异步构建索引"""
    global build_status, searcher
    
    # 重置状态
    build_status["is_building"] = True
    build_status["progress"] = 0
    build_status["total"] = 0
    build_status["message"] = "正在扫描图像..."
    
    try:
        # 1. 扫描数据集
        dataset_manager = ImageDatasetManager(str(DATASET_DIR))
        image_paths = dataset_manager.get_all_images()
        
        if len(image_paths) == 0:
            build_status["message"] = "数据集中没有图像"
            build_status["progress"] = 0
            build_status["total"] = 0
            build_status["is_building"] = False
            return
        
        build_status["total"] = len(image_paths)
        build_status["message"] = f"找到 {len(image_paths)} 张图像，开始提取特征..."
        
        # 2. 提取特征
        extractor = ImageFeatureExtractor()
        features_list = []
        valid_paths = []
        
        for i, path in enumerate(image_paths):
            try:
                feature = extractor.extract(path)
                features_list.append(feature)
                valid_paths.append(path)
                build_status["progress"] = i + 1
                
                if (i + 1) % 10 == 0 or (i + 1) == len(image_paths):
                    build_status["message"] = f"已处理 {i + 1}/{len(image_paths)} 张图像..."
                
                # 小延迟避免阻塞
                await asyncio.sleep(0.01)
                
            except Exception as e:
                print(f"处理图像失败 {path}: {e}")
                continue
        
        if len(features_list) == 0:
            build_status["message"] = "没有成功处理任何图像"
            build_status["is_building"] = False
            return
        
        # 3. 构建索引
        build_status["message"] = "正在构建 Faiss 索引..."
        import numpy as np
        features = np.array(features_list)
        
        index_manager = FaissIndexManager()
        index_manager.build_index(features, valid_paths)
        
        # 4. 保存索引
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        index_manager.save(str(INDEX_PATH), str(PATHS_PATH))
        
        # 5. 重新加载索引
        load_index()
        
        # 构建成功，重置进度显示
        build_status["message"] = f"索引构建完成！包含 {len(valid_paths)} 个向量"
        build_status["last_build_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        build_status["progress"] = build_status["total"]  # 确保进度显示100%
        
        print(f"✅ 索引构建完成: {len(valid_paths)} 个向量")
        
    except Exception as e:
        build_status["message"] = f"构建失败: {str(e)}"
        print(f"❌ 构建索引失败: {e}")
    finally:
        # 延迟重置构建状态，让前端有时间获取最终状态
        await asyncio.sleep(2)
        build_status["is_building"] = False
        print("✅ 构建状态已重置")


@app.post("/api/dataset/build")
async def build_dataset_index(background_tasks: BackgroundTasks):
    """
    构建数据集索引
    """
    if build_status["is_building"]:
        raise HTTPException(status_code=400, detail="正在构建索引中")
    
    # 在后台任务中构建索引
    background_tasks.add_task(build_index_async)
    
    return {
        "success": True,
        "message": "开始构建索引"
    }


@app.post("/api/search")
async def search_image(
    image: UploadFile = File(...),
    topk: int = Form(5)
):
    """
    图像搜索接口
    
    - **image**: 上传的查询图像
    - **topk**: 返回结果数量（默认5）
    """
    if searcher is None or searcher.index_manager is None or searcher.index_manager.index is None:
        raise HTTPException(status_code=503, detail="索引未加载，请先构建索引")
    
    # 保存上传的图像到临时目录
    temp_path = TEMP_DIR / f"query_{int(time.time())}_{image.filename}"
    
    try:
        # 保存上传的文件
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
        
        # 执行搜索
        start_time = time.time()
        results = searcher.search(str(temp_path), topk)
        search_time = (time.time() - start_time) * 1000
        
        if results is None:
            raise HTTPException(status_code=500, detail="搜索失败")
        
        # 构建响应
        response_results = []
        for result in results:
            response_results.append({
                "rank": int(result["rank"]),
                "path": str(result["path"]),
                "distance": float(result["distance"]),
                "similarity": float(result["similarity"]),
                "url": f"/api/image/{result['path'].replace('/', '___')}"
            })
        
        return {
            "success": True,
            "data": {
                "query_image": str(temp_path),
                "results": response_results,
                "total": len(response_results),
                "time_ms": round(search_time, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")
    finally:
        image.file.close()


@app.get("/api/image/{image_path:path}")
async def get_image(image_path: str):
    """
    获取图像文件
    
    - **image_path**: 图像路径（使用 ___ 代替 /）
    """
    decoded_path = image_path.replace("___", "/")
    full_path = Path(__file__).parent.parent / decoded_path
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="图像不存在")
    
    return FileResponse(str(full_path))


@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "图像检索系统 API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "dataset": "/api/dataset/*",
            "search": "POST /api/search",
            "image": "/api/image/{path}"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
