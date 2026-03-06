import numpy as np
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models


class _ImageDataset(Dataset):
    def __init__(self, image_paths, transform):
        self.image_paths = image_paths
        self.transform = transform

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        path = self.image_paths[idx]
        try:
            image = Image.open(path).convert('RGB')
            return self.transform(image), idx
        except Exception:
            return torch.zeros(3, 224, 224), -1


class ImageFeatureExtractor:
    """图像特征提取器，使用预训练的ResNet50模型"""

    def __init__(self):
        # 加载预训练的ResNet50模型
        self.model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        # 移除最后的分类层，获取特征向量
        self.model = torch.nn.Sequential(*list(self.model.children())[:-1])
        self.model.eval()

        # 图像预处理
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])

        # 设备选择
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.model.to(self.device)

    def extract(self, image_path):
        """提取单张图像的特征向量"""
        try:
            image = Image.open(image_path).convert('RGB')
            image = self.transform(image).unsqueeze(0)
            image = image.to(self.device)

            with torch.no_grad():
                feature = self.model(image)

            # 将特征转换为numpy数组并展平
            feature = feature.cpu().numpy().flatten()
            # L2归一化
            feature = feature / np.linalg.norm(feature)
            return feature
        except Exception as e:
            print(f"提取特征失败 {image_path}: {e}")
            return None

    def extract_batch(self, image_paths, batch_size=32):
        """批量提取图像特征（使用DataLoader并行加载）"""
        dataset = _ImageDataset(image_paths, self.transform)
        loader = DataLoader(dataset, batch_size=batch_size, num_workers=0, pin_memory=False)

        features = [None] * len(image_paths)
        valid_paths = []

        print(f"正在提取 {len(image_paths)} 张图像的特征...")
        processed = 0
        with torch.no_grad():
            for images, indices in loader:
                images = images.to(self.device)
                batch_features = self.model(images).cpu().numpy()
                batch_features = batch_features.reshape(batch_features.shape[0], -1)

                for feat, idx in zip(batch_features, indices.numpy()):
                    if idx == -1:
                        continue
                    norm = np.linalg.norm(feat)
                    if norm > 0:
                        features[idx] = feat / norm

                processed += len(indices)
                print(f"进度: {processed}/{len(image_paths)}")

        valid_features = []
        for i, feat in enumerate(features):
            if feat is not None:
                valid_features.append(feat)
                valid_paths.append(image_paths[i])

        return np.array(valid_features), valid_paths
