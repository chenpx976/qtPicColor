"""颜色分析模块"""

import time
from typing import List
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from sklearn.utils import shuffle

from .models import ColorInfo, ImageInfo


class ColorAnalyzer:
    """颜色分析器"""
    
    def __init__(self, max_colors: int = 16, sample_fraction: float = 0.1):
        """
        初始化颜色分析器
        
        Args:
            max_colors: 最大提取颜色数量
            sample_fraction: 采样比例，用于加速大图像处理
        """
        self.max_colors = max_colors
        self.sample_fraction = sample_fraction
    
    def analyze_image(self, image_path: str) -> ImageInfo:
        """
        分析图像颜色
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            ImageInfo: 包含颜色分析结果的图像信息
        """
        start_time = time.time()
        
        # 加载图像
        with Image.open(image_path) as image:
            # 转换为 RGB 格式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 获取图像信息
            width, height = image.size
            format_name = image.format or 'Unknown'
            
            # 提取颜色
            colors = self.extract_dominant_colors(image)
            
        # 计算分析时间
        analysis_time = time.time() - start_time
        
        # 获取文件大小
        import os
        size_bytes = os.path.getsize(image_path)
        
        return ImageInfo(
            file_path=image_path,
            width=width,
            height=height,
            format=format_name,
            size_bytes=size_bytes,
            colors=colors,
            analysis_time=analysis_time
        )
    
    def extract_dominant_colors(self, image: Image) -> List[ColorInfo]:
        """
        使用 K-means 算法提取主要颜色
        
        Args:
            image: PIL Image 对象
            
        Returns:
            List[ColorInfo]: 颜色信息列表，按占比降序排列
        """
        # 调整图像大小以优化性能
        image = self._resize_for_analysis(image)
        
        # 将图像转换为像素数组
        pixels = np.array(image).reshape(-1, 3)
        
        # 如果图像较大，进行采样以提高性能
        if len(pixels) > 50000:
            pixels = shuffle(pixels, random_state=42, n_samples=int(len(pixels) * self.sample_fraction))
        
        # 确定实际的聚类数量（不能超过像素点数量）
        n_colors = min(self.max_colors, len(np.unique(pixels.view(np.dtype((np.void, pixels.dtype.itemsize*pixels.shape[1]))))))
        
        if n_colors <= 1:
            # 如果只有一种颜色，直接返回
            rgb = tuple(map(int, pixels[0]))
            hex_code = self._rgb_to_hex(rgb)
            return [ColorInfo(
                rgb=rgb,
                hex_code=hex_code,
                percentage=100.0,
                pixel_count=len(pixels)
            )]
        
        # 执行 K-means 聚类
        kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
        labels = kmeans.fit_predict(pixels)
        
        # 计算每个聚类的统计信息
        colors = []
        total_pixels = len(pixels)
        
        for i, center in enumerate(kmeans.cluster_centers_):
            mask = labels == i
            pixel_count = np.sum(mask)
            percentage = (pixel_count / total_pixels) * 100
            
            rgb = tuple(map(int, center))
            hex_code = self._rgb_to_hex(rgb)
            
            colors.append(ColorInfo(
                rgb=rgb,
                hex_code=hex_code,
                percentage=percentage,
                pixel_count=pixel_count
            ))
        
        # 按占比降序排列
        return sorted(colors, key=lambda x: x.percentage, reverse=True)
    
    def _resize_for_analysis(self, image: Image, max_size: int = 800) -> Image:
        """
        调整图像大小以优化分析性能
        
        Args:
            image: PIL Image 对象
            max_size: 最大尺寸
            
        Returns:
            Image: 调整大小后的图像
        """
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image
    
    @staticmethod
    def _rgb_to_hex(rgb: tuple) -> str:
        """
        RGB 转十六进制颜色值
        
        Args:
            rgb: RGB 元组
            
        Returns:
            str: 十六进制颜色值
        """
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}".upper() 