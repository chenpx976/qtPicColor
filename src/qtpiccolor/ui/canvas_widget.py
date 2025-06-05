"""颜色画布组件"""

import math
from typing import List, Optional, Tuple
from PyQt6.QtWidgets import QWidget, QToolTip
from PyQt6.QtCore import pyqtSignal, Qt, QRect, QPoint
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QMouseEvent

from ..core.models import ColorInfo
from ..utils.clipboard import ClipboardManager


class CanvasWidget(QWidget):
    """颜色分布画布组件"""

    # 信号定义
    color_clicked = pyqtSignal(str)  # 颜色点击信号，传递十六进制颜色值

    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors: List[ColorInfo] = []
        self.color_rects: List[Tuple[QRect, ColorInfo]] = (
            []
        )  # 存储颜色矩形和对应的颜色信息
        self.hovered_color: Optional[ColorInfo] = None

        self.setFixedSize(1024, 1024)
        self.setStyleSheet(
            """
            QWidget {
                background-color: white;
                border: 1px solid #ddd;
            }
        """
        )

        # 启用鼠标跟踪以支持悬停效果
        self.setMouseTracking(True)

    def set_colors(self, colors: List[ColorInfo]):
        """
        设置要显示的颜色列表

        Args:
            colors: 颜色信息列表
        """
        self.colors = colors
        self.calculate_layout()
        self.update()  # 重绘画布

    def calculate_layout(self):
        """计算颜色块的布局"""
        self.color_rects.clear()

        if not self.colors:
            return

        canvas_size = min(self.width(), self.height())
        total_area = canvas_size * canvas_size

        # 使用网格布局算法
        self._calculate_grid_layout(total_area, canvas_size)

    def _calculate_grid_layout(self, total_area: int, canvas_size: int):
        """
        计算网格布局

        Args:
            total_area: 画布总面积
            canvas_size: 画布尺寸
        """
        # 计算网格尺寸
        num_colors = len(self.colors)
        grid_size = math.ceil(math.sqrt(num_colors))
        cell_size = canvas_size // grid_size

        for i, color in enumerate(self.colors):
            row = i // grid_size
            col = i % grid_size

            # 根据颜色占比调整矩形大小
            base_size = cell_size
            scale_factor = (
                math.sqrt(color.percentage / 100) * 0.8 + 0.2
            )  # 保持最小20%大小
            rect_size = int(base_size * scale_factor)

            # 计算位置，使矩形在格子中居中
            x = col * cell_size + (cell_size - rect_size) // 2
            y = row * cell_size + (cell_size - rect_size) // 2

            rect = QRect(x, y, rect_size, rect_size)
            self.color_rects.append((rect, color))

    def paintEvent(self, event):
        """绘制颜色分布"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))

        if not self.color_rects:
            # 如果没有颜色数据，显示提示
            self._draw_empty_state(painter)
            return

        # 绘制颜色块
        for rect, color_info in self.color_rects:
            self._draw_color_block(painter, rect, color_info)

        # 绘制悬停效果
        if self.hovered_color:
            self._draw_hover_effect(painter)

    def _draw_color_block(self, painter: QPainter, rect: QRect, color_info: ColorInfo):
        """
        绘制单个颜色块

        Args:
            painter: QPainter 对象
            rect: 颜色块矩形
            color_info: 颜色信息
        """
        # 设置颜色
        color = QColor(*color_info.rgb)
        painter.fillRect(rect, color)

        # 绘制边框
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(rect)

        # 如果颜色块足够大，显示百分比文字
        if rect.width() > 60 and rect.height() > 40:
            self._draw_color_text(painter, rect, color_info)

    def _draw_color_text(self, painter: QPainter, rect: QRect, color_info: ColorInfo):
        """
        在颜色块上绘制文字信息

        Args:
            painter: QPainter 对象
            rect: 颜色块矩形
            color_info: 颜色信息
        """
        # 根据颜色亮度选择文字颜色
        brightness = sum(color_info.rgb) / 3
        text_color = QColor(255, 255, 255) if brightness < 128 else QColor(0, 0, 0)

        painter.setPen(text_color)

        # 设置字体
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)

        # 绘制百分比
        percentage_text = f"{color_info.percentage:.1f}%"
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, percentage_text)

    def _draw_empty_state(self, painter: QPainter):
        """绘制空状态提示"""
        painter.setPen(QColor(150, 150, 150))
        font = QFont()
        font.setPointSize(16)
        painter.setFont(font)

        text = "请上传图片开始颜色分析"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, text)

    def _draw_hover_effect(self, painter: QPainter):
        """绘制悬停效果"""
        # 找到悬停的颜色块
        for rect, color_info in self.color_rects:
            if color_info == self.hovered_color:
                # 绘制高亮边框
                painter.setPen(QPen(QColor(255, 255, 0), 3))
                painter.drawRect(rect.adjusted(-2, -2, 2, 2))
                break

    def mousePressEvent(self, event: QMouseEvent):
        """处理鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            clicked_color = self._get_color_at_position(event.position().toPoint())
            if clicked_color:
                # 复制颜色值到剪贴板
                ClipboardManager.copy_text(clicked_color.hex_code)
                self.color_clicked.emit(clicked_color.hex_code)

                # 显示复制成功提示
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"已复制: {clicked_color.hex_code}",
                    self,
                )

    def mouseMoveEvent(self, event: QMouseEvent):
        """处理鼠标移动事件"""
        hovered_color = self._get_color_at_position(event.position().toPoint())

        if hovered_color != self.hovered_color:
            self.hovered_color = hovered_color
            self.update()  # 重绘以显示/隐藏悬停效果

            # 显示颜色信息工具提示
            if hovered_color:
                tooltip_text = (
                    f"颜色: {hovered_color.hex_code}\n"
                    f"RGB: {hovered_color.rgb}\n"
                    f"占比: {hovered_color.percentage:.1f}%\n"
                    f"点击复制颜色值"
                )
                QToolTip.showText(event.globalPosition().toPoint(), tooltip_text, self)
            else:
                QToolTip.hideText()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        if self.hovered_color:
            self.hovered_color = None
            self.update()
        QToolTip.hideText()

    def _get_color_at_position(self, position: QPoint) -> Optional[ColorInfo]:
        """
        获取指定位置的颜色信息

        Args:
            position: 鼠标位置

        Returns:
            Optional[ColorInfo]: 如果位置有颜色块则返回颜色信息，否则返回 None
        """
        for rect, color_info in self.color_rects:
            if rect.contains(position):
                return color_info
        return None
