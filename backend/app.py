"""
FastAPI 后端服务
提供图像搜索 API
"""
import os
import sys
import time
import shutil
from pathlib import Path
from typing import List, Optional

# 解决 OpenMP 冲突
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# 添加父目录到路径以导入 searcher
sys.path.insert(0, str(Path(__file__).parent.parent))
from searcher import ImageSearcher

# 创建 FastAPI 应用
app = FastAPI(
    title="图像检索系统 API",
    description="基于 Faiss 的以图搜图后端服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
searcher = None
INDEX_PATH = Path(__file__).parent.parent / "index" / "image_index.faiss"
PATHS_PATH = Path(__file__).parent.parent / "index" / "image_paths.pkl"
TEMP_DIR = Path(__file__).parent.parent / "temp"

# 确保临时目录存在
TEMP_DIR.mkdir(exist_ok=True)


@app.on_event("startup")
async def startup_event():
    """启动时加载索引"""
    global searcher
    try:
        searcher = ImageSearcher()
        if INDEX_PATH.exists() and PATHS_PATH.exists():
            searcher.load_index(str(INDEX_PATH), str(PATHS_PATH))
            print(f"✅ 索引加载成功，包含 {searcher.index_manager.index.ntotal} 个向量")
        else:
            print("⚠️ 索引文件不存在，请先构建索引")
    except Exception as e:
        print(f"❌ 索引加载失败: {e}")
        searcher = None


@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "index_loaded": searcher is not None and searcher.index_manager.index is not None,
        "image_count": searcher.index_manager.index.ntotal if searcher and searcher.index_manager.index else 0
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
    if searcher is None or searcher.index_manager.index is None:
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
        search_time = (time.time() - start_time) * 1000  # 转换为毫秒
        
        if results is None:
            raise HTTPException(status_code=500, detail="搜索失败")
        
        # 构建响应（将 numpy 类型转换为 Python 原生类型）
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
    # 解码路径
    decoded_path = image_path.replace("___", "/")
    
    # 构建完整路径
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
            "search": "POST /api/search",
            "image": "/api/image/{path}"
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
