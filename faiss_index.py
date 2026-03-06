import os
import pickle
import faiss
import numpy as np


class FaissIndexManager:
    """Faiss索引管理器"""
    
    def __init__(self, dimension=2048):
        self.dimension = dimension
        self.index = None
        self.image_paths = []
    
    def build_index(self, features, image_paths, use_ivf=False):
        """构建Faiss索引"""
        print(f"构建索引，向量维度: {self.dimension}, 向量数量: {len(features)}")
        
        if use_ivf and len(features) > 100:
            # 使用IVF索引，适合大规模数据集
            nlist = min(100, len(features) // 10)
            quantizer = faiss.IndexFlatL2(self.dimension)
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
            self.index.train(features.astype('float32'))
        else:
            # 使用精确检索，适合小规模数据集
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.index.add(features.astype('float32'))
        self.image_paths = image_paths
        print(f"索引构建完成，包含 {self.index.ntotal} 个向量")
    
    def save(self, index_path, paths_path):
        """保存索引和图像路径"""
        os.makedirs(os.path.dirname(os.path.abspath(index_path)), exist_ok=True)
        faiss.write_index(self.index, index_path)
        with open(paths_path, 'wb') as f:
            pickle.dump(self.image_paths, f)
        print(f"索引已保存到 {index_path}")
        print(f"图像路径已保存到 {paths_path}")
    
    def load(self, index_path, paths_path):
        """加载索引和图像路径"""
        self.index = faiss.read_index(index_path)
        with open(paths_path, 'rb') as f:
            self.image_paths = pickle.load(f)
        print(f"索引加载完成，包含 {self.index.ntotal} 个向量")
        return True
    
    def search(self, query_feature, top_k=5):
        """搜索相似图像"""
        query_feature = query_feature.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_feature, top_k)
        return distances[0], indices[0]
