"""剪贴板操作工具"""

from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QMimeData, QBuffer, QIODevice
from PIL import Image
import io
import numpy as np


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
        try:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()

            if mime_data.hasImage():
                # 方法1：尝试直接获取QImage
                qimage = clipboard.image()
                if not qimage.isNull():
                    pil_image = ClipboardManager._qimage_to_pil_improved(qimage)
                    if pil_image:
                        return pil_image

                # 方法2：尝试从QPixmap获取
                pixmap = clipboard.pixmap()
                if not pixmap.isNull():
                    qimage = pixmap.toImage()
                    pil_image = ClipboardManager._qimage_to_pil_improved(qimage)
                    if pil_image:
                        return pil_image

            # 方法3：尝试从原始数据获取
            if mime_data.hasFormat("image/png"):
                png_data = mime_data.data("image/png")
                if png_data:
                    return ClipboardManager._bytes_to_pil(png_data.data())

            if mime_data.hasFormat("image/jpeg"):
                jpeg_data = mime_data.data("image/jpeg")
                if jpeg_data:
                    return ClipboardManager._bytes_to_pil(jpeg_data.data())

            if mime_data.hasFormat("image/bmp"):
                bmp_data = mime_data.data("image/bmp")
                if bmp_data:
                    return ClipboardManager._bytes_to_pil(bmp_data.data())

        except Exception as e:
            print(f"从剪贴板获取图像失败: {e}")

        return None

    @staticmethod
    def has_image() -> bool:
        """
        检查剪贴板是否包含图像

        Returns:
            bool: 剪贴板是否包含图像
        """
        try:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()

            # 检查多种图像格式
            return (
                mime_data.hasImage()
                or mime_data.hasFormat("image/png")
                or mime_data.hasFormat("image/jpeg")
                or mime_data.hasFormat("image/bmp")
                or mime_data.hasFormat("image/gif")
            )
        except Exception:
            return False

    @staticmethod
    def _qimage_to_pil_improved(qimage: QImage) -> Optional[Image.Image]:
        """
        改进的QImage转PIL Image方法

        Args:
            qimage: QImage 对象

        Returns:
            Optional[Image.Image]: PIL Image 对象
        """
        try:
            if qimage.isNull():
                return None

            # 方法1：使用QBuffer转换（推荐）
            buffer = QBuffer()
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)

            # 保存为PNG格式到缓冲区
            if qimage.save(buffer, "PNG"):
                buffer.close()
                png_data = buffer.data().data()
                return Image.open(io.BytesIO(png_data))

            # 方法2：直接内存转换（备用）
            width = qimage.width()
            height = qimage.height()

            # 转换为RGBA格式以确保兼容性
            if qimage.format() != QImage.Format.Format_RGBA8888:
                qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)

            # 获取图像数据
            ptr = qimage.constBits()
            ptr.setsize(qimage.sizeInBytes())

            # 使用numpy数组作为中介
            arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))

            # 转换为PIL Image（RGBA格式）
            pil_image = Image.fromarray(arr, "RGBA")

            # 如果需要，转换为RGB
            if pil_image.mode == "RGBA":
                # 创建白色背景
                background = Image.new("RGB", pil_image.size, (255, 255, 255))
                background.paste(
                    pil_image, mask=pil_image.split()[-1]
                )  # 使用alpha通道作为mask
                return background

            return pil_image

        except Exception as e:
            print(f"QImage转PIL失败: {e}")
            return None

    @staticmethod
    def _qimage_to_pil(qimage: QImage) -> Image.Image:
        """
        将 QImage 转换为 PIL Image（保留原方法作为备用）

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

    @staticmethod
    def _bytes_to_pil(data: bytes) -> Optional[Image.Image]:
        """
        从字节数据创建PIL Image

        Args:
            data: 图像字节数据

        Returns:
            Optional[Image.Image]: PIL Image 对象
        """
        try:
            return Image.open(io.BytesIO(data))
        except Exception as e:
            print(f"从字节数据创建PIL Image失败: {e}")
            return None
