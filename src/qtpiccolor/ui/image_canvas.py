"""图像画布组件"""

import os
from typing import List, Optional, Tuple
import numpy as np
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QToolTip,
)
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QPoint, QSize, QTimer
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QMouseEvent, QPixmap, QBrush

from ..core.models import ColorInfo, ImageInfo
from ..utils.clipboard import ClipboardManager


class ImageCanvas(QWidget):
    """图像画布组件，显示原图并叠加颜色分析结果"""

    # 信号定义
    colorClicked = pyqtSignal(str)  # 颜色点击信号，传递十六进制颜色值

    def __init__(self, parent=None):
        super().__init__(parent)
        self._imageInfo: Optional[ImageInfo] = None
        self._originalPixmap: Optional[QPixmap] = None
        self._displayPixmap: Optional[QPixmap] = None
        self._highlightedPixmap: Optional[QPixmap] = None  # 高亮显示的图像
        self._scaleFactor = 1.0
        self._showColorMarkers = True
        self._hoveredColor: Optional[ColorInfo] = None
        self._selectedColor: Optional[str] = None  # 选中的颜色HEX值

        # 延迟更新定时器，避免频繁重绘
        self._updateTimer = QTimer()
        self._updateTimer.setSingleShot(True)
        self._updateTimer.timeout.connect(self._delayedUpdate)

        self._setupUi()

    def _setupUi(self):
        """设置用户界面"""
        self.setMinimumSize(600, 400)

        # 设置背景色
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(248, 249, 250))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 启用鼠标跟踪以支持悬停效果
        self.setMouseTracking(True)

    def setImageInfo(self, imageInfo: ImageInfo):
        """
        设置图像信息并显示

        Args:
            imageInfo: 图像信息对象
        """
        self._imageInfo = imageInfo
        self._selectedColor = None  # 重置选中的颜色
        self._highlightedPixmap = None
        if imageInfo is None:
            self._originalPixmap = None
            self._displayPixmap = None
            self.update()
            return

        self._loadImage()
        self._updateDisplay()

    def _loadImage(self):
        """加载图像"""
        if not self._imageInfo or not os.path.exists(self._imageInfo.file_path):
            self._originalPixmap = None
            self._displayPixmap = None
            self.update()
            return

        # 使用PIL加载图片，然后转换为QPixmap确保兼容性
        try:
            from PIL import Image
            from PyQt6.QtGui import QImage

            # 使用PIL加载原图
            pilImage = Image.open(self._imageInfo.file_path)

            # 确保是RGB模式
            if pilImage.mode != "RGB":
                pilImage = pilImage.convert("RGB")

            # 转换为numpy数组
            npArray = np.array(pilImage)
            height, width, channels = npArray.shape

            # 创建QImage
            qimage = QImage(
                npArray.data,
                width,
                height,
                width * channels,
                QImage.Format.Format_RGB888,
            )

            # 创建QPixmap
            self._originalPixmap = QPixmap.fromImage(qimage)

        except Exception as e:
            print(f"PIL加载失败，尝试直接加载: {e}")
            # 回退到直接加载
            self._originalPixmap = QPixmap(self._imageInfo.file_path)

        if self._originalPixmap.isNull():
            print(f"无法加载图片: {self._imageInfo.file_path}")
            self._originalPixmap = None
            self._displayPixmap = None
            self.update()
            return

        print(
            f"图片加载成功: {self._originalPixmap.width()}x{self._originalPixmap.height()}"
        )

        # 计算适合窗口的缩放比例
        self._calculateScaleFactor()
        self._updateDisplay()

    def _calculateScaleFactor(self):
        """计算缩放比例"""
        if not self._originalPixmap:
            return

        # 获取当前可用空间
        availableWidth = max(self.width() - 40, 400)  # 减去边距
        availableHeight = max(self.height() - 40, 300)

        print(f"可用空间: {availableWidth}x{availableHeight}")
        print(
            f"原图尺寸: {self._originalPixmap.width()}x{self._originalPixmap.height()}"
        )

        # 计算缩放比例
        scaleX = availableWidth / self._originalPixmap.width()
        scaleY = availableHeight / self._originalPixmap.height()

        # 选择较小的比例，确保图片完全显示
        self._scaleFactor = min(scaleX, scaleY)

        # 设定合理的缩放范围：0.1到3.0
        self._scaleFactor = max(0.1, min(self._scaleFactor, 3.0))

        # 如果缩放后的图片太小，适当放大
        minDisplaySize = 200
        scaledWidth = self._originalPixmap.width() * self._scaleFactor
        scaledHeight = self._originalPixmap.height() * self._scaleFactor

        if scaledWidth < minDisplaySize or scaledHeight < minDisplaySize:
            scaleForMinSize = minDisplaySize / min(
                self._originalPixmap.width(), self._originalPixmap.height()
            )
            self._scaleFactor = max(self._scaleFactor, scaleForMinSize)

        # 最终限制缩放比例
        self._scaleFactor = max(0.1, min(self._scaleFactor, 3.0))

        print(f"计算的缩放比例: {self._scaleFactor}")

    def _updateDisplay(self):
        """更新显示"""
        if not self._originalPixmap:
            self._displayPixmap = None
            self.setFixedSize(600, 400)
            self.update()
            return

        # 计算缩放后的尺寸
        scaledWidth = int(self._originalPixmap.width() * self._scaleFactor)
        scaledHeight = int(self._originalPixmap.height() * self._scaleFactor)

        print(f"缩放后尺寸: {scaledWidth}x{scaledHeight}")

        # 使用最高质量的缩放算法
        self._displayPixmap = self._originalPixmap.scaled(
            scaledWidth,
            scaledHeight,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # 设置画布大小，为颜色标记和边距留出空间
        margin = 30
        canvasWidth = max(self._displayPixmap.width() + margin * 2, 600)
        canvasHeight = max(self._displayPixmap.height() + margin * 2, 400)

        self.setFixedSize(canvasWidth, canvasHeight)
        print(f"画布尺寸: {canvasWidth}x{canvasHeight}")

        self.update()

    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 绘制背景
        painter.fillRect(self.rect(), QColor(248, 249, 250))

        if not self._displayPixmap:
            self._drawEmptyState(painter)
            return

        # 计算图像绘制位置（居中）
        imgRect = QRect(
            (self.width() - self._displayPixmap.width()) // 2,
            (self.height() - self._displayPixmap.height()) // 2,
            self._displayPixmap.width(),
            self._displayPixmap.height(),
        )

        # 绘制图像阴影效果
        shadowRect = imgRect.adjusted(2, 2, 2, 2)
        painter.fillRect(shadowRect, QColor(0, 0, 0, 30))

        # 绘制图像（如果有高亮图像则使用高亮版本）
        if self._highlightedPixmap and self._selectedColor:
            # 高亮模式：只显示选中颜色部分，使用PS风格的棋盘格透明背景
            self._drawTransparencyGrid(painter, imgRect)

            # 绘制高亮图像（带透明效果）
            scaled_highlight = self._highlightedPixmap.scaled(
                self._displayPixmap.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceOver
            )
            painter.drawPixmap(imgRect, scaled_highlight)
        else:
            # 正常模式：显示完整图像
            painter.drawPixmap(imgRect, self._displayPixmap)

        # 绘制图像边框
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(imgRect)

        # 绘制颜色标记（只在非高亮模式下显示）
        if (
            self._showColorMarkers
            and self._imageInfo
            and self._imageInfo.colors
            and not (self._highlightedPixmap and self._selectedColor)
        ):
            self._drawColorMarkers(painter, imgRect)

        # 绘制悬停效果
        if self._hoveredColor:
            self._drawHoverEffect(painter, imgRect)

    def _drawEmptyState(self, painter: QPainter):
        """绘制空状态"""
        painter.setPen(QColor(150, 150, 150))
        font = QFont()
        font.setPointSize(16)
        painter.setFont(font)

        text = "请上传图片开始颜色分析"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

    def _drawColorMarkers(self, painter: QPainter, imgRect: QRect):
        """
        绘制颜色标记

        Args:
            painter: QPainter 对象
            imgRect: 图像绘制区域
        """
        for i, colorInfo in enumerate(
            self._imageInfo.colors[:12]
        ):  # 最多显示前12个颜色
            if not colorInfo.position:
                continue

            # 计算标记位置（根据缩放比例调整）
            markerX = imgRect.x() + int(colorInfo.position[0] * self._scaleFactor)
            markerY = imgRect.y() + int(colorInfo.position[1] * self._scaleFactor)

            # 确保标记在图像范围内
            if not imgRect.contains(markerX, markerY):
                continue

            # 根据颜色占比确定标记大小
            baseSize = 16
            sizeFactor = min(colorInfo.percentage / 100 * 3 + 0.5, 2.0)
            markerSize = int(baseSize * sizeFactor)
            markerSize = max(12, min(markerSize, 32))  # 限制大小范围

            # 绘制标记
            self._drawSingleMarker(
                painter, markerX, markerY, markerSize, colorInfo, i + 1
            )

    def _drawSingleMarker(
        self,
        painter: QPainter,
        x: int,
        y: int,
        size: int,
        colorInfo: ColorInfo,
        index: int,
    ):
        """
        绘制单个颜色标记

        Args:
            painter: QPainter 对象
            x, y: 标记位置
            size: 标记大小
            colorInfo: 颜色信息
            index: 颜色序号
        """
        center = QPoint(x, y)
        radius = size // 2

        # 绘制外圈阴影
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 50)))
        painter.drawEllipse(
            center.x() - radius + 1, center.y() - radius + 1, size, size
        )

        # 绘制外圈（白色边框）
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QBrush(QColor(*colorInfo.rgb)))
        painter.drawEllipse(center, radius, radius)

        # 绘制内圈边框
        painter.setPen(QPen(QColor(0, 0, 0, 80), 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius - 1, radius - 1)

        # 绘制序号（如果标记足够大）
        if size >= 20:
            # 根据颜色亮度选择文字颜色
            brightness = sum(colorInfo.rgb) / 3
            textColor = QColor(255, 255, 255) if brightness < 128 else QColor(0, 0, 0)

            painter.setPen(textColor)
            font = QFont()
            font.setPointSize(max(7, size // 3))
            font.setBold(True)
            painter.setFont(font)

            textRect = QRect(x - radius, y - radius, size, size)
            painter.drawText(textRect, Qt.AlignmentFlag.AlignCenter, str(index))

    def _drawHoverEffect(self, painter: QPainter, imgRect: QRect):
        """绘制悬停效果"""
        if not self._hoveredColor or not self._hoveredColor.position:
            return

        # 计算悬停标记位置
        markerX = imgRect.x() + int(self._hoveredColor.position[0] * self._scaleFactor)
        markerY = imgRect.y() + int(self._hoveredColor.position[1] * self._scaleFactor)

        # 绘制高亮圈
        painter.setPen(QPen(QColor(255, 193, 7), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(markerX, markerY), 20, 20)

        # 绘制脉冲效果
        painter.setPen(QPen(QColor(255, 193, 7, 100), 2))
        painter.drawEllipse(QPoint(markerX, markerY), 25, 25)

    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            clickedColor = self._getColorAtPosition(event.position().toPoint())
            if clickedColor:
                # 复制颜色值到剪贴板
                ClipboardManager.copy_text(clickedColor.hex_code)
                self.colorClicked.emit(clickedColor.hex_code)

                # 显示复制成功提示
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"已复制: {clickedColor.hex_code}\n占比: {clickedColor.percentage:.1f}%",
                    self,
                    QRect(),
                    2000,  # 显示2秒
                )

    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件"""
        hoveredColor = self._getColorAtPosition(event.position().toPoint())

        if hoveredColor != self._hoveredColor:
            self._hoveredColor = hoveredColor
            # 使用定时器延迟更新，避免频繁重绘
            self._updateTimer.start(50)

            # 显示颜色信息工具提示
            if hoveredColor:
                tipText = (
                    f"颜色: {hoveredColor.hex_code}\n"
                    f"RGB: {hoveredColor.rgb}\n"
                    f"占比: {hoveredColor.percentage:.1f}%"
                )
                QToolTip.showText(event.globalPosition().toPoint(), tipText, self)
            else:
                QToolTip.hideText()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self._hoveredColor = None
        self.update()
        QToolTip.hideText()

    def _delayedUpdate(self):
        """延迟更新"""
        self.update()

    def _getColorAtPosition(self, position: QPoint) -> Optional[ColorInfo]:
        """
        获取指定位置的颜色信息

        Args:
            position: 鼠标位置

        Returns:
            ColorInfo: 颜色信息，如果没有找到则返回None
        """
        if not self._imageInfo or not self._displayPixmap:
            return None

        # 计算图像绘制区域
        imgRect = QRect(
            (self.width() - self._displayPixmap.width()) // 2,
            (self.height() - self._displayPixmap.height()) // 2,
            self._displayPixmap.width(),
            self._displayPixmap.height(),
        )

        # 检查是否在图像区域内
        if not imgRect.contains(position):
            return None

        # 检查是否在颜色标记附近
        for colorInfo in self._imageInfo.colors:
            if not colorInfo.position:
                continue

            # 计算标记位置
            markerX = imgRect.x() + int(colorInfo.position[0] * self._scaleFactor)
            markerY = imgRect.y() + int(colorInfo.position[1] * self._scaleFactor)

            # 计算距离
            distance = (
                (position.x() - markerX) ** 2 + (position.y() - markerY) ** 2
            ) ** 0.5

            # 根据颜色占比确定检测范围
            baseRange = 12
            rangeFactor = min(colorInfo.percentage / 100 * 2 + 0.8, 2.5)
            detectionRange = baseRange * rangeFactor

            if distance <= detectionRange:
                return colorInfo

        return None

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self._originalPixmap:
            # 延迟重新计算，避免频繁调整
            self._updateTimer.start(100)

    def _delayedResizeUpdate(self):
        """延迟的大小调整更新"""
        if self._originalPixmap:
            self._calculateScaleFactor()
            self._updateDisplay()

    def toggleColorMarkers(self, show: bool):
        """切换颜色标记显示"""
        self._showColorMarkers = show
        self.update()

    def highlightColor(self, hex_color: str):
        """
        高亮指定颜色

        Args:
            hex_color: 要高亮的颜色HEX值
        """
        self._selectedColor = hex_color
        self._createHighlightedPixmap()
        self.update()

    def clearHighlight(self):
        """清除颜色高亮"""
        self._selectedColor = None
        self._highlightedPixmap = None
        self.update()

    def _createHighlightedPixmap(self):
        """创建高亮显示的图像"""
        if not self._originalPixmap or not self._selectedColor:
            self._highlightedPixmap = None
            return

        try:
            from PIL import Image
            from PyQt6.QtGui import QImage

            # 重新加载原图进行处理
            pilImage = Image.open(self._imageInfo.file_path)
            if pilImage.mode != "RGB":
                pilImage = pilImage.convert("RGB")

            # 转换为numpy数组
            img_array = np.array(pilImage)

            # 解析选中的颜色
            selected_rgb = self._hex_to_rgb(self._selectedColor)

            # 创建蒙版：找到与选中颜色相似的像素
            mask = self._create_color_mask(img_array, selected_rgb, threshold=30)

            # 创建RGBA图像（带透明通道）
            height, width = img_array.shape[:2]
            highlighted_array = np.zeros((height, width, 4), dtype=np.uint8)

            # 只在匹配的像素位置显示原始颜色
            highlighted_array[mask, :3] = img_array[mask]  # RGB通道
            highlighted_array[mask, 3] = 255  # Alpha通道，完全不透明
            # 非匹配区域的Alpha通道保持0（完全透明）

            # 转换回QPixmap，使用正确的格式
            qimage = QImage(
                highlighted_array.data,
                width,
                height,
                width * 4,
                QImage.Format.Format_RGBA8888,
            )
            self._highlightedPixmap = QPixmap.fromImage(qimage)

            print(f"创建高亮图像: {width}x{height}, 匹配像素数: {np.sum(mask)}")

        except Exception as e:
            print(f"创建高亮图像失败: {e}")
            self._highlightedPixmap = None

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """将HEX颜色转换为RGB"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _create_color_mask(
        self, img_array: np.ndarray, target_rgb: tuple, threshold: int = 30
    ) -> np.ndarray:
        """
        创建颜色蒙版

        Args:
            img_array: 图像数组
            target_rgb: 目标RGB颜色
            threshold: 颜色相似度阈值

        Returns:
            np.ndarray: 布尔蒙版，True表示相似颜色
        """
        # 计算每个像素与目标颜色的距离
        target = np.array(target_rgb)
        distances = np.linalg.norm(img_array - target, axis=2)

        # 返回距离小于阈值的像素蒙版
        return distances < threshold

    def _drawTransparencyGrid(self, painter: QPainter, rect: QRect):
        """
        绘制PS风格的透明背景棋盘格

        Args:
            painter: QPainter对象
            rect: 绘制区域
        """
        grid_size = 16  # 每个格子的大小
        light_color = QColor(255, 255, 255)  # 浅色格子
        dark_color = QColor(204, 204, 204)  # 深色格子

        # 保存当前画笔状态
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)

        # 绘制棋盘格
        for y in range(rect.top(), rect.bottom(), grid_size):
            for x in range(rect.left(), rect.right(), grid_size):
                # 计算当前格子应该是浅色还是深色
                grid_x = (x - rect.left()) // grid_size
                grid_y = (y - rect.top()) // grid_size
                is_light = (grid_x + grid_y) % 2 == 0

                # 选择颜色
                color = light_color if is_light else dark_color
                painter.setBrush(QBrush(color))

                # 计算格子大小，确保不超出边界
                width = min(grid_size, rect.right() - x)
                height = min(grid_size, rect.bottom() - y)

                # 绘制格子
                painter.drawRect(x, y, width, height)

        # 恢复画笔状态
        painter.restore()


class ImageCanvasContainer(QScrollArea):
    """图像画布容器，提供滚动功能"""

    colorClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._canvas = ImageCanvas()
        self._canvas.colorClicked.connect(self.colorClicked)

        self.setWidget(self._canvas)
        self.setWidgetResizable(False)  # 不自动调整大小
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 设置滚动条策略
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 设置背景色
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(248, 249, 250))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 设置滚动条样式
        self._setupScrollBarStyle()

    def _setupScrollBarStyle(self):
        """设置滚动条样式"""
        self.setStyleSheet(
            """
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background-color: #f1f1f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #a8a8a8;
            }
            QScrollBar:horizontal {
                background-color: #f1f1f1;
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: #c1c1c1;
                border-radius: 6px;
                min-width: 20px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #a8a8a8;
            }
        """
        )

    def setImageInfo(self, imageInfo: ImageInfo):
        """设置图像信息"""
        self._canvas.setImageInfo(imageInfo)

    def toggleColorMarkers(self, show: bool):
        """切换颜色标记显示"""
        self._canvas.toggleColorMarkers(show)

    def highlightColor(self, hex_color: str):
        """高亮指定颜色"""
        self._canvas.highlightColor(hex_color)

    def clearHighlight(self):
        """清除颜色高亮"""
        self._canvas.clearHighlight()

    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        if self._canvas._originalPixmap:
            # 延迟重新计算，避免频繁调整
            self._canvas._updateTimer.start(100)

    def _delayedResizeUpdate(self):
        """延迟的大小调整更新"""
        if self._canvas._originalPixmap:
            self._canvas._calculateScaleFactor()
            self._canvas._updateDisplay()
