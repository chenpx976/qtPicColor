"""剪贴板操作工具"""

from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QMimeData
from PIL import Image
import io


class ClipboardManager:
    """剪贴板管理器"""
    
    @staticmethod
    def copy_text(text: str) -> None:
        """
        复制文本到剪贴板
        
        Args:
            text: 要复制的文本
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
    
    @staticmethod
    def get_image() -> Optional[Image.Image]:
        """
        从剪贴板获取图像
        
        Returns:
            Optional[Image.Image]: PIL Image 对象，如果剪贴板中没有图像则返回 None
        """
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        
        if mime_data.hasImage():
            # 获取 QImage
            qimage = clipboard.image()
            if not qimage.isNull():
                return ClipboardManager._qimage_to_pil(qimage)
        
        return None
    
    @staticmethod
    def has_image() -> bool:
        """
        检查剪贴板是否包含图像
        
        Returns:
            bool: 剪贴板是否包含图像
        """
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        return mime_data.hasImage()
    
    @staticmethod
    def _qimage_to_pil(qimage: QImage) -> Image.Image:
        """
        将 QImage 转换为 PIL Image
        
        Args:
            qimage: QImage 对象
            
        Returns:
            Image.Image: PIL Image 对象
        """
        # 确保图像格式为 RGB
        if qimage.format() != QImage.Format.Format_RGB888:
            qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        
        # 获取图像数据
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.constBits()
        ptr.setsize(qimage.sizeInBytes())
        
        # 创建 PIL Image
        pil_image = Image.frombuffer("RGB", (width, height), ptr, "raw", "RGB", 0, 1)
        return pil_image.copy()  # 复制以避免内存问题 