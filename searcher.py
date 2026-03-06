import os

# 解决 OpenMP 冲突问题
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

from feature_extractor import ImageFeatureExtractor
from dataset_manager import ImageDatasetManager
from faiss_index import FaissIndexManager


class ImageSearcher:
    """图像搜索主类"""
    
    def __init__(self):
        self.feature_extractor = ImageFeatureExtractor()
        self.dataset_manager = None
        self.index_manager = FaissIndexManager()
    
    def build_index(self, data_dir, index_path, paths_path, use_ivf=False):
        """构建图像索引"""
        # 扫描图像
        self.dataset_manager = ImageDatasetManager(data_dir)
        image_paths = self.dataset_manager.scan_images()
        
        if len(image_paths) == 0:
            print("未找到图像文件！")
            return False
        
        # 提取特征
        features, valid_paths = self.feature_extractor.extract_batch(image_paths)
        
        if len(features) == 0:
            print("特征提取失败！")
            return False
        
        # 构建索引
        self.index_manager.build_index(features, valid_paths, use_ivf)
        
        # 保存索引
        self.index_manager.save(index_path, paths_path)
        return True
    
    def load_index(self, index_path, paths_path):
        """加载已有索引"""
        return self.index_manager.load(index_path, paths_path)
    
    def search(self, query_image_path, top_k=5):
        """搜索相似图像"""
        # 提取查询图像特征
        query_feature = self.feature_extractor.extract(query_image_path)
        if query_feature is None:
            print("查询图像特征提取失败！")
            return None
        
        # 搜索
        distances, indices = self.index_manager.search(query_feature, top_k)
        
        # 获取结果路径
        results = []
        for i, (dist, idx) in enumerate(zip(distances, indices)):
            if idx < len(self.index_manager.image_paths):
                results.append({
                    'rank': i + 1,
                    'path': self.index_manager.image_paths[idx],
                    'distance': dist,
                    'similarity': 1 - dist / 2  # 余弦相似度（特征已L2归一化）
                })
        
        return results
    
    def show_results(self, query_path, results, save_path=None):
        """展示搜索结果"""
        if results is None or len(results) == 0:
            print("没有搜索结果！")
            return
        
        try:
            n_results = len(results)
            fig, axes = plt.subplots(1, n_results + 1, figsize=(4 * (n_results + 1), 4))
            
            # 显示查询图像
            query_img = Image.open(query_path)
            axes[0].imshow(query_img)
            axes[0].set_title('Query Image')
            axes[0].axis('off')
            
            # 显示搜索结果
            for i, result in enumerate(results):
                img = Image.open(result['path'])
                axes[i + 1].imshow(img)
                axes[i + 1].set_title(f"Rank {result['rank']}\nDist: {result['distance']:.4f}\nSim: {result['similarity']:.4f}")
                axes[i + 1].axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"结果已保存到 {save_path}")
            else:
                try:
                    matplotlib.use('TkAgg')
                    plt.show()
                except Exception:
                    print("当前环境无法显示图形界面，请使用 --save_result 参数保存结果图像")
        except Exception as e:
            print(f"展示结果时出错: {e}")
            if save_path:
                print(f"尝试保存结果到 {save_path} 失败")
