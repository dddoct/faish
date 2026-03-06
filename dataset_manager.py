import os


class ImageDatasetManager:
    """图像数据集管理器"""

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.image_paths = []
        self.supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')

    def scan_images(self):
        """扫描目录中的所有图像文件"""
        self.image_paths = []
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                if file.lower().endswith(self.supported_formats):
                    self.image_paths.append(os.path.join(root, file))

        print(f"找到 {len(self.image_paths)} 张图像")
        return self.image_paths

    def get_all_images(self):
        """获取所有图像路径（兼容方法）"""
        if not self.image_paths:
            return self.scan_images()
        return self.image_paths
