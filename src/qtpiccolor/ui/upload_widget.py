"""图片上传组件"""

import tempfile
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                             QFileDialog, QMessageBox, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QKeySequence, QFont

from ..utils.file_handler import FileHandler
from ..utils.clipboard import ClipboardManager


class UploadWidget(QFrame):
    """图片上传组件"""
    
    # 信号定义
    image_uploaded = pyqtSignal(str)  # 图片上传成功信号，传递文件路径
    upload_error = pyqtSignal(str)    # 上传错误信号，传递错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_drag_drop()
        
    def setup_ui(self):
        """设置用户界面"""
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                border-color: #007ACC;
                background-color: #f0f8ff;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题标签
        title_label = QLabel("上传图片")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333333; border: none;")
        
        # 提示标签
        hint_label = QLabel("拖拽图片到此处\n或点击下方按钮选择文件\n支持 Ctrl+V 粘贴剪贴板图片")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("""
            color: #666666; 
            border: none; 
            line-height: 1.5;
            font-size: 14px;
        """)
        
        # 选择文件按钮
        self.select_button = QPushButton("选择图片文件")
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004785;
            }
        """)
        self.select_button.clicked.connect(self.select_file)
        
        # 粘贴按钮
        self.paste_button = QPushButton("粘贴剪贴板图片 (Ctrl+V)")
        self.paste_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        self.paste_button.clicked.connect(self.paste_from_clipboard)
        
        # 支持格式标签
        format_label = QLabel("支持格式: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP")
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        format_label.setStyleSheet("""
            color: #888888; 
            border: none; 
            font-size: 12px;
        """)
        
        # 布局
        layout.addWidget(title_label)
        layout.addWidget(hint_label)
        layout.addWidget(self.select_button)
        layout.addWidget(self.paste_button)
        layout.addWidget(format_label)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMinimumSize(400, 300)
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            # 检查是否包含图片文件
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if FileHandler.is_image_file(file_path):
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def dragMoveEvent(self, event):
        """处理拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """处理文件拖拽释放事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if FileHandler.is_image_file(file_path):
                        self.load_image_file(file_path)
                        event.acceptProposedAction()
                        return
        event.ignore()
    
    def select_file(self):
        """打开文件选择对话框"""
        file_filter = "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;所有文件 (*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择图片文件", 
            "", 
            file_filter
        )
        
        if file_path:
            self.load_image_file(file_path)
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴图片"""
        try:
            if not ClipboardManager.has_image():
                QMessageBox.information(self, "提示", "剪贴板中没有图片")
                return
            
            image = ClipboardManager.get_image()
            if image:
                # 将剪贴板图片保存为临时文件
                temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                image.save(temp_file.name, 'PNG')
                temp_file.close()
                
                self.load_image_file(temp_file.name)
            else:
                QMessageBox.warning(self, "错误", "无法获取剪贴板中的图片")
                
        except Exception as e:
            error_msg = f"粘贴图片失败: {str(e)}"
            self.upload_error.emit(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def load_image_file(self, file_path: str):
        """
        加载图片文件
        
        Args:
            file_path: 图片文件路径
        """
        try:
            # 验证文件
            if not FileHandler.is_image_file(file_path):
                raise ValueError("不支持的文件格式")
            
            if not FileHandler.validate_image_size(file_path, max_size_mb=50.0):
                raise ValueError("文件太大，请选择小于 50MB 的图片")
            
            # 尝试加载图片以验证有效性
            FileHandler.load_image(file_path)
            
            # 发送成功信号
            self.image_uploaded.emit(file_path)
            
        except Exception as e:
            error_msg = f"加载图片失败: {str(e)}"
            self.upload_error.emit(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        # 支持 Ctrl+V 粘贴
        if event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event) 