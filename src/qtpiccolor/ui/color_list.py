"""颜色列表组件"""

from typing import List
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QListWidgetItem, QPushButton, 
                             QFrame, QComboBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor, QPalette

from ..core.models import ColorInfo
from ..utils.clipboard import ClipboardManager


class ColorListWidget(QWidget):
    """颜色列表组件"""
    
    # 信号定义
    color_selected = pyqtSignal(str)  # 颜色选择信号，传递十六进制颜色值
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors: List[ColorInfo] = []
        self.current_format = "HEX"  # 当前显示的颜色格式
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # 标题和格式选择
        header_layout = QHBoxLayout()
        
        title_label = QLabel("颜色列表")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        # 颜色格式选择器
        self.format_combo = QComboBox()
        self.format_combo.addItems(["HEX", "RGB", "HSL", "HSV"])
        self.format_combo.setCurrentText(self.current_format)
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("格式:"))
        header_layout.addWidget(self.format_combo)
        
        # 颜色列表
        self.color_list = QListWidget()
        self.color_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
            }
            QListWidget::item:selected {
                background-color: #bbdefb;
            }
        """)
        self.color_list.setAlternatingRowColors(True)
        self.color_list.itemClicked.connect(self.on_color_item_clicked)
        
        # 空状态标签
        self.empty_label = QLabel("请上传图片开始颜色分析")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #666;
            font-size: 14px;
            padding: 40px;
        """)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.copy_all_button = QPushButton("复制所有颜色")
        self.copy_all_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004785;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """)
        self.copy_all_button.clicked.connect(self.copy_all_colors)
        self.copy_all_button.setEnabled(False)
        
        self.clear_button = QPushButton("清空列表")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
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
                background-color: #ccc;
                color: #888;
            }
        """)
        self.clear_button.clicked.connect(self.clear_colors)
        self.clear_button.setEnabled(False)
        
        button_layout.addWidget(self.copy_all_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        
        # 布局
        layout.addLayout(header_layout)
        layout.addWidget(self.color_list)
        layout.addWidget(self.empty_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setMinimumWidth(300)
        
        # 初始状态
        self.show_empty_state()
    
    def set_colors(self, colors: List[ColorInfo]):
        """
        设置颜色列表
        
        Args:
            colors: 颜色信息列表
        """
        self.colors = colors
        self.refresh_display()
        
        if colors:
            self.show_color_list()
        else:
            self.show_empty_state()
    
    def refresh_display(self):
        """刷新显示"""
        self.color_list.clear()
        
        for i, color_info in enumerate(self.colors):
            item = QListWidgetItem()
            widget = ColorItemWidget(color_info, self.current_format, i + 1)
            widget.color_clicked.connect(self.on_color_widget_clicked)
            
            item.setSizeHint(widget.sizeHint())
            self.color_list.addItem(item)
            self.color_list.setItemWidget(item, widget)
    
    def show_color_list(self):
        """显示颜色列表"""
        self.color_list.setVisible(True)
        self.empty_label.setVisible(False)
        self.copy_all_button.setEnabled(True)
        self.clear_button.setEnabled(True)
    
    def show_empty_state(self):
        """显示空状态"""
        self.color_list.setVisible(False)
        self.empty_label.setVisible(True)
        self.copy_all_button.setEnabled(False)
        self.clear_button.setEnabled(False)
    
    def on_format_changed(self, format_text: str):
        """格式改变处理"""
        self.current_format = format_text
        self.refresh_display()
    
    def on_color_item_clicked(self, item: QListWidgetItem):
        """颜色项点击处理"""
        widget = self.color_list.itemWidget(item)
        if widget:
            color_value = widget.get_current_color_value()
            ClipboardManager.copy_text(color_value)
            self.color_selected.emit(color_value)
    
    def on_color_widget_clicked(self, color_value: str):
        """颜色组件点击处理"""
        ClipboardManager.copy_text(color_value)
        self.color_selected.emit(color_value)
    
    def copy_all_colors(self):
        """复制所有颜色值"""
        if not self.colors:
            return
        
        color_values = []
        for color_info in self.colors:
            if self.current_format == "HEX":
                color_values.append(color_info.hex_code)
            elif self.current_format == "RGB":
                color_values.append(f"rgb{color_info.rgb}")
            elif self.current_format == "HSL":
                hsl = color_info.hsl
                color_values.append(f"hsl({hsl[0]:.0f}, {hsl[1]:.1f}%, {hsl[2]:.1f}%)")
            elif self.current_format == "HSV":
                hsv = color_info.hsv
                color_values.append(f"hsv({hsv[0]:.0f}, {hsv[1]:.1f}%, {hsv[2]:.1f}%)")
        
        all_colors_text = "\n".join(color_values)
        ClipboardManager.copy_text(all_colors_text)
    
    def clear_colors(self):
        """清空颜色列表"""
        self.colors.clear()
        self.color_list.clear()
        self.show_empty_state()


class ColorItemWidget(QWidget):
    """单个颜色项组件"""
    
    color_clicked = pyqtSignal(str)  # 颜色点击信号
    
    def __init__(self, color_info: ColorInfo, format_type: str, index: int, parent=None):
        super().__init__(parent)
        self.color_info = color_info
        self.format_type = format_type
        self.index = index
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)
        
        # 序号
        index_label = QLabel(f"{self.index}.")
        index_label.setFixedWidth(20)
        index_label.setStyleSheet("color: #666; font-weight: bold;")
        
        # 颜色预览块
        color_preview = QLabel()
        color_preview.setFixedSize(40, 30)
        color_preview.setStyleSheet(f"""
            background-color: {self.color_info.hex_code};
            border: 1px solid #ccc;
            border-radius: 4px;
        """)
        
        # 颜色信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # 颜色值
        color_value = self.get_current_color_value()
        color_label = QLabel(color_value)
        color_font = QFont("Monaco", 11)  # 等宽字体
        color_label.setFont(color_font)
        color_label.setStyleSheet("font-weight: bold; color: #333;")
        
        # 百分比
        percentage_label = QLabel(f"{self.color_info.percentage:.1f}%")
        percentage_label.setStyleSheet("color: #666; font-size: 12px;")
        
        info_layout.addWidget(color_label)
        info_layout.addWidget(percentage_label)
        
        # 复制按钮
        copy_button = QPushButton("复制")
        copy_button.setFixedSize(50, 25)
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        copy_button.clicked.connect(lambda: self.color_clicked.emit(color_value))
        
        # 布局
        layout.addWidget(index_label)
        layout.addWidget(color_preview)
        layout.addLayout(info_layout)
        layout.addStretch()
        layout.addWidget(copy_button)
        
        self.setLayout(layout)
        self.setFixedHeight(50)
    
    def get_current_color_value(self) -> str:
        """获取当前格式的颜色值"""
        if self.format_type == "HEX":
            return self.color_info.hex_code
        elif self.format_type == "RGB":
            return f"rgb{self.color_info.rgb}"
        elif self.format_type == "HSL":
            hsl = self.color_info.hsl
            return f"hsl({hsl[0]:.0f}, {hsl[1]:.1f}%, {hsl[2]:.1f}%)"
        elif self.format_type == "HSV":
            hsv = self.color_info.hsv
            return f"hsv({hsv[0]:.0f}, {hsv[1]:.1f}%, {hsv[2]:.1f}%)"
        else:
            return self.color_info.hex_code 