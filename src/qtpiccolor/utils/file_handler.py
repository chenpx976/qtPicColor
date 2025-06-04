"""文件处理工具"""

from pathlib import Path
from typing import Optional
from PIL import Image


class FileHandler:
    """文件处理工具类"""
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """
        检查是否为支持的图像文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为支持的图像文件
        """
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_FORMATS
    
    @staticmethod
    def load_image(file_path: str) -> Image.Image:
        """
        加载图像文件
        
        Args:
            file_path: 图像文件路径
            
        Returns:
            Image: PIL Image 对象
            
        Raises:
            ValueError: 当文件无法加载时
        """
        try:
            if not Path(file_path).exists():
                raise ValueError(f"文件不存在: {file_path}")
            
            if not FileHandler.is_image_file(file_path):
                raise ValueError(f"不支持的文件格式: {Path(file_path).suffix}")
            
            image = Image.open(file_path)
            # 验证图像是否可以正常加载
            image.verify()
            # 重新打开图像（verify 会关闭文件）
            image = Image.open(file_path)
            return image
            
        except Exception as e:
            raise ValueError(f"无法加载图像 {file_path}: {str(e)}")
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        获取文件大小（MB）
        
        Args:
            file_path: 文件路径
            
        Returns:
            float: 文件大小（MB）
        """
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    
    @staticmethod
    def validate_image_size(file_path: str, max_size_mb: float = 50.0) -> bool:
        """
        验证图像文件大小
        
        Args:
            file_path: 文件路径
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            bool: 文件大小是否符合要求
        """
        return FileHandler.get_file_size_mb(file_path) <= max_size_mb 