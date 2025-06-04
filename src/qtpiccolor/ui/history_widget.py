"""历史记录组件"""

import os
from typing import List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QScrollArea, QMessageBox, 
                             QSizePolicy, QSpacerItem)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QCursor

from ..core.models import HistoryRecord
from ..core.history_manager import HistoryManager


class HistoryWidget(QWidget):
    """历史记录组件"""
    
    # 信号定义
    recordSelected = pyqtSignal(HistoryRecord)  # 选择历史记录
    recordDeleted = pyqtSignal(str)  # 删除历史记录
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._historyManager = HistoryManager()
        self._itemWidgets = []  # 存储所有历史记录项组件
        self._setupUi()
        self.refreshHistory()
    
    def _setupUi(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 标题和操作按钮
        headerLayout = QHBoxLayout()
        
        titleLabel = QLabel("历史记录")
        titleFont = QFont()
        titleFont.setPointSize(16)
        titleFont.setBold(True)
        titleLabel.setFont(titleFont)
        
        # 清空按钮
        self._clearAllButton = QPushButton("清空全部")
        self._clearAllButton.setMinimumSize(80, 30)
        self._clearAllButton.clicked.connect(self._clearAllHistory)
        self._setupClearButtonStyle()
        
        headerLayout.addWidget(titleLabel)
        headerLayout.addStretch()
        headerLayout.addWidget(self._clearAllButton)
        
        # 滚动区域
        self._scrollArea = QScrollArea()
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scrollArea.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #dee2e6;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #adb5bd;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #6c757d;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        # 滚动内容容器
        self._scrollContent = QWidget()
        self._scrollContent.setStyleSheet("background-color: #ffffff;")  # 设置白色背景
        self._scrollLayout = QVBoxLayout(self._scrollContent)
        self._scrollLayout.setSpacing(10)  # 增加项目间距
        self._scrollLayout.setContentsMargins(10, 10, 10, 10)  # 增加边距
        
        # 添加弹性空间到底部
        self._scrollLayout.addStretch()
        
        self._scrollArea.setWidget(self._scrollContent)
        
        # 空状态标签
        self._emptyLabel = QLabel("暂无历史记录\n\n上传图片后会自动保存到历史记录中")
        self._emptyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._emptyLabel.setMinimumHeight(200)
        
        # 设置空状态标签样式
        emptyFont = QFont()
        emptyFont.setPointSize(14)
        self._emptyLabel.setFont(emptyFont)
        self._emptyLabel.setStyleSheet("""
            QLabel {
                color: #6c757d;
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                padding: 40px;
                margin: 20px;
            }
        """)
        
        # 布局
        layout.addLayout(headerLayout)
        layout.addWidget(self._scrollArea)
        layout.addWidget(self._emptyLabel)
        
        self.setMinimumWidth(320)
    
    def _setupClearButtonStyle(self):
        """设置清空按钮样式"""
        self._clearAllButton.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #888888;
            }
        """)
    
    def addRecord(self, imageInfo):
        """添加新的历史记录"""
        record = self._historyManager.add_record(imageInfo)
        self.refreshHistory()
        return record
    
    def refreshHistory(self):
        """刷新历史记录显示"""
        # 清除现有的组件
        self._clearScrollContent()
        
        records = self._historyManager.get_records(limit=50)
        
        if not records:
            self._showEmptyState()
            return
        
        self._showHistoryList()
        
        # 添加历史记录项
        for record in records:
            widget = HistoryItemWidget(record)
            widget.itemClicked.connect(lambda r=record: self.recordSelected.emit(r))
            widget.deleteClicked.connect(self._deleteRecord)
            
            # 插入到弹性空间之前
            self._scrollLayout.insertWidget(self._scrollLayout.count() - 1, widget)
            self._itemWidgets.append(widget)
    
    def _clearScrollContent(self):
        """清除滚动内容"""
        # 移除所有历史记录项组件
        for widget in self._itemWidgets:
            self._scrollLayout.removeWidget(widget)
            widget.deleteLater()
        self._itemWidgets.clear()
    
    def _showHistoryList(self):
        """显示历史记录列表"""
        self._scrollArea.setVisible(True)
        self._emptyLabel.setVisible(False)
        self._clearAllButton.setEnabled(True)
    
    def _showEmptyState(self):
        """显示空状态"""
        self._scrollArea.setVisible(False)
        self._emptyLabel.setVisible(True)
        self._clearAllButton.setEnabled(False)
    
    def _deleteRecord(self, recordId: str):
        """删除历史记录"""
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除这条历史记录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self._historyManager.remove_record(recordId)
            if success:
                self.refreshHistory()
                self.recordDeleted.emit(recordId)
    
    def _clearAllHistory(self):
        """清空所有历史记录"""
        reply = QMessageBox.question(
            self, 
            "确认清空", 
            "确定要清空所有历史记录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._historyManager.clear_all()
            self.refreshHistory()


class HistoryItemWidget(QFrame):
    """历史记录单项组件"""
    
    itemClicked = pyqtSignal()
    deleteClicked = pyqtSignal(str)
    
    def __init__(self, record: HistoryRecord, parent=None):
        super().__init__(parent)
        self._record = record
        self._setupUi()
    
    def _setupUi(self):
        """设置用户界面"""
        # 设置框架样式
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        # 设置固定高度和大小策略
        self.setFixedHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # 设置样式
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin: 4px 2px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #007acc;
            }
        """)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)  # 增加内边距
        layout.setSpacing(15)
        
        # 缩略图
        thumbnailLabel = self._createThumbnailLabel()
        
        # 信息区域
        infoWidget = self._createInfoWidget()
        
        # 删除按钮
        deleteButton = self._createDeleteButton()
        
        # 添加到布局
        layout.addWidget(thumbnailLabel)
        layout.addWidget(infoWidget, 1)
        layout.addWidget(deleteButton, 0, Qt.AlignmentFlag.AlignTop)
    
    def _createThumbnailLabel(self) -> QLabel:
        """创建缩略图标签"""
        thumbnailLabel = QLabel()
        thumbnailLabel.setFixedSize(80, 80)
        thumbnailLabel.setStyleSheet("""
            QLabel {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: #f5f5f5;
            }
        """)
        
        # 加载缩略图
        if self._record.thumbnail_path and os.path.exists(self._record.thumbnail_path):
            pixmap = QPixmap(self._record.thumbnail_path)
            if not pixmap.isNull():
                scaledPixmap = pixmap.scaled(
                    78, 78, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                thumbnailLabel.setPixmap(scaledPixmap)
                thumbnailLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                self._setNoImageText(thumbnailLabel)
        else:
            self._setNoImageText(thumbnailLabel)
        
        return thumbnailLabel
    
    def _setNoImageText(self, label: QLabel):
        """设置无图片文本"""
        label.setText("无图片")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        label.setFont(font)
        label.setStyleSheet(label.styleSheet() + "color: #999999;")
    
    def _createInfoWidget(self) -> QWidget:
        """创建信息组件"""
        infoWidget = QWidget()
        infoLayout = QVBoxLayout(infoWidget)
        infoLayout.setSpacing(6)  # 增加间距
        infoLayout.setContentsMargins(0, 5, 0, 5)  # 增加上下边距
        
        # 文件名
        displayName = self._record.display_name
        if len(displayName) > 28:
            displayName = displayName[:25] + "..."
        
        nameLabel = QLabel(displayName)
        nameFont = QFont()
        nameFont.setPointSize(13)
        nameFont.setBold(True)
        nameLabel.setFont(nameFont)
        nameLabel.setStyleSheet("color: #333333; margin-bottom: 2px;")
        nameLabel.setWordWrap(False)
        nameLabel.setMinimumHeight(20)  # 确保最小高度
        
        # 图片信息
        infoText = f"{self._record.image_info.width}×{self._record.image_info.height} | {self._record.file_size_mb:.1f}MB"
        sizeLabel = QLabel(infoText)
        sizeLabel.setStyleSheet("color: #666666; font-size: 11px; margin-bottom: 2px;")
        sizeLabel.setMinimumHeight(16)
        
        # 颜色数量
        colorsText = f"提取了 {self._record.color_count} 种颜色"
        colorsLabel = QLabel(colorsText)
        colorsLabel.setStyleSheet("color: #666666; font-size: 11px; margin-bottom: 2px;")
        colorsLabel.setMinimumHeight(16)
        
        # 时间
        timeText = self._record.created_at.strftime("%Y-%m-%d %H:%M:%S")
        timeLabel = QLabel(timeText)
        timeLabel.setStyleSheet("color: #999999; font-size: 10px;")
        timeLabel.setMinimumHeight(14)
        
        # 添加到布局
        infoLayout.addWidget(nameLabel)
        infoLayout.addWidget(sizeLabel)
        infoLayout.addWidget(colorsLabel)
        infoLayout.addStretch()
        infoLayout.addWidget(timeLabel)
        
        return infoWidget
    
    def _createDeleteButton(self) -> QPushButton:
        """创建删除按钮"""
        deleteButton = QPushButton("×")
        deleteButton.setFixedSize(24, 24)
        deleteButton.clicked.connect(lambda: self.deleteClicked.emit(self._record.id))
        
        deleteButton.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        return deleteButton
    
    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.itemClicked.emit()
        super().mousePressEvent(event)
    
    def getRecord(self) -> HistoryRecord:
        """获取历史记录"""
        return self._record 