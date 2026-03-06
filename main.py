import os

# 解决 OpenMP 冲突问题（必须在导入其他库之前设置）
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import argparse
from searcher import ImageSearcher


def main():
    parser = argparse.ArgumentParser(description='基于Faiss的以图搜图工具')
    parser.add_argument('--build', action='store_true', help='构建索引')
    parser.add_argument('--search', action='store_true', help='执行搜索')
    parser.add_argument('--data_dir', default='data/images', help='图像数据集目录')
    parser.add_argument('--index_path', default='index/image_index.faiss', help='索引文件路径')
    parser.add_argument('--paths_path', default='index/image_paths.pkl', help='图像路径文件')
    parser.add_argument('--query', help='查询图像路径')
    parser.add_argument('--topk', type=int, default=5, help='返回结果数量')
    parser.add_argument('--use_ivf', action='store_true', help='使用IVF索引')
    parser.add_argument('--save_result', help='保存结果图像路径')
    
    args = parser.parse_args()
    
    searcher = ImageSearcher()
    
    # 构建索引
    if args.build:
        print("=" * 50)
        print("开始构建索引...")
        print("=" * 50)
        success = searcher.build_index(
            args.data_dir,
            args.index_path,
            args.paths_path,
            args.use_ivf
        )
        if not success:
            return
        print("=" * 50)
        print("索引构建完成！")
        print("=" * 50)
    
    # 执行搜索
    if args.search:
        if not args.query:
            print("请指定查询图像路径：--query <image_path>")
            return
        
        # 如果索引不存在，先构建
        if not os.path.exists(args.index_path):
            print("索引文件不存在，先构建索引...")
            success = searcher.build_index(
                args.data_dir,
                args.index_path,
                args.paths_path,
                args.use_ivf
            )
            if not success:
                return
        else:
            # 加载已有索引
            searcher.load_index(args.index_path, args.paths_path)
        
        print("=" * 50)
        print(f"搜索图像: {args.query}")
        print("=" * 50)
        
        # 执行搜索
        results = searcher.search(args.query, args.topk)
        
        if results:
            print("\n搜索结果:")
            for result in results:
                print(f"Rank {result['rank']}: {result['path']}")
                print(f"  距离: {result['distance']:.4f}, 相似度: {result['similarity']:.4f}")
            
            # 展示结果
            searcher.show_results(args.query, results, args.save_result)


if __name__ == '__main__':
    main()
