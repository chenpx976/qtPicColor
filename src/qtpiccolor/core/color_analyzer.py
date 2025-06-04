"""颜色分析模块"""

import time
import os
from typing import List, Dict
from collections import Counter
import numpy as np
from PIL import Image

from .models import ColorInfo, ImageInfo


class ColorAnalyzer:
    """颜色分析器 - 直接统计图片中所有颜色的像素数量"""
    
    def __init__(self, max_colors: int = 16, min_pixels: int = 100):
        """
        初始化颜色分析器
        
        Args:
            max_colors: 最大返回颜色数量
            min_pixels: 最小像素数量阈值，低于此值的颜色将被忽略
        """
        self.max_colors = max_colors
        self.min_pixels = min_pixels
    
    def analyze_image(self, image_path: str) -> ImageInfo:
        """
        分析图像颜色
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            ImageInfo: 包含颜色分析结果的图像信息
        """
        start_time = time.time()
        
        # 获取图像基本信息
        with Image.open(image_path) as image:
            width, height = image.size
            format_name = image.format or 'Unknown'
        
        # 提取颜色
        colors = self.extract_colors_by_pixel_count(image_path)
        
        # 计算分析时间
        analysis_time = time.time() - start_time
        
        # 获取文件大小
        size_bytes = os.path.getsize(image_path)
        
        return ImageInfo(
            file_path=image_path,
            width=width,
            height=height,
            size_bytes=size_bytes,
            colors=colors,
            analysis_time=analysis_time,
            format=format_name
        )
    
    def extract_colors_by_pixel_count(self, image_path: str) -> List[ColorInfo]:
        """
        通过统计像素数量提取颜色
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            List[ColorInfo]: 按像素数量排序的颜色信息列表
        """
        try:
            # 打开图像并转换为RGB
            with Image.open(image_path) as image:
                # 转换为RGB模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 如果图像太大，先缩小以提高性能
                max_size = 800
                if max(image.size) > max_size:
                    ratio = max_size / max(image.size)
                    new_size = (int(image.width * ratio), int(image.height * ratio))
                    image = image.resize(new_size, Image.Resampling.LANCZOS)
                
                # 转换为numpy数组
                img_array = np.array(image)
                
                # 重塑为二维数组，每行是一个像素的RGB值
                pixels = img_array.reshape(-1, 3)
                
                # 统计每种颜色的像素数量
                color_counts = self._count_colors(pixels)
                
                # 过滤掉像素数量太少的颜色
                filtered_colors = {
                    color: count for color, count in color_counts.items() 
                    if count >= self.min_pixels
                }
                
                # 如果过滤后颜色太少，降低阈值
                if len(filtered_colors) < 3:
                    min_threshold = max(1, self.min_pixels // 10)
                    filtered_colors = {
                        color: count for color, count in color_counts.items() 
                        if count >= min_threshold
                    }
                
                # 按像素数量排序
                sorted_colors = sorted(filtered_colors.items(), key=lambda x: x[1], reverse=True)
                
                # 转换为ColorInfo对象
                colors = []
                total_pixels = len(pixels)
                
                for i, (rgb, pixel_count) in enumerate(sorted_colors[:self.max_colors]):
                    # 计算百分比
                    percentage = (pixel_count / total_pixels) * 100
                    
                    # 确保RGB值是标准Python int类型，避免numpy类型问题
                    rgb = tuple(int(c) for c in rgb)
                    
                    # 转换为HEX
                    hex_code = self._rgb_to_hex(rgb)
                    
                    colors.append(ColorInfo(
                        rgb=rgb,
                        hex_code=hex_code,
                        percentage=float(percentage),  # 确保是标准float类型
                        position=(0, 0)  # 简化位置信息
                    ))
                
                return colors
                
        except Exception as e:
            print(f"颜色提取失败: {e}")
            return [self._create_default_color()]
    
    def _count_colors(self, pixels: np.ndarray) -> Dict[tuple, int]:
        """
        统计颜色出现次数
        
        Args:
            pixels: 像素数组，形状为 (n_pixels, 3)
            
        Returns:
            Dict[tuple, int]: 颜色到像素数量的映射
        """
        # 将每个像素转换为元组，然后统计
        pixel_tuples = [tuple(pixel) for pixel in pixels]
        return Counter(pixel_tuples)
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """
        RGB 转十六进制颜色值
        
        Args:
            rgb: RGB 元组
            
        Returns:
            str: 十六进制颜色值
        """
        return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"
    
    def _create_default_color(self) -> ColorInfo:
        """
        创建默认颜色
        
        Returns:
            ColorInfo: 默认的灰色
        """
        return ColorInfo(
            rgb=(128, 128, 128),
            hex_code="#808080",
            percentage=100.0,
            position=(0, 0)
        ) 