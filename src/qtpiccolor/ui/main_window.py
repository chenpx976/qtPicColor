"""主窗口"""

import os
import time
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QMenuBar, QStatusBar, QMessageBox, 
                             QProgressBar, QLabel, QScrollArea, QTabWidget, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from .upload_widget import UploadWidget
from .image_canvas import ImageCanvasContainer
from .color_list import ColorListWidget
from .history_widget import HistoryWidget
from ..core.color_analyzer import ColorAnalyzer
from ..core.models import ImageInfo


class AnalysisThread(QThread):
    """颜色分析线程"""
    
    analysis_finished = pyqtSignal(object)  # ImageInfo
    analysis_error = pyqtSignal(str)
    
    def __init__(self, image_path: str, max_colors: int = 16):
        super().__init__()
        self.image_path = image_path
        self.max_colors = max_colors
        self.analyzer = ColorAnalyzer(max_colors=max_colors)
    
    def run(self):
        """执行颜色分析"""
        try:
            image_info = self.analyzer.analyze_image(self.image_path)
            self.analysis_finished.emit(image_info)
        except Exception as e:
            self.analysis_error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_image_info: Optional[ImageInfo] = None
        self.analysis_thread: Optional[AnalysisThread] = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_connections()
        
        # 初始状态：显示右侧面板，默认显示历史记录标签页
        self.right_tabs.setCurrentIndex(1)  # 设置历史记录为默认标签页
        
        # 定时器用于清理临时文件
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self.cleanup_temp_files)
        self.cleanup_timer.start(300000)  # 5分钟清理一次
    
    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("qtPicColor - 图片颜色分析工具")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主要布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 左侧面板（上传和图像显示）
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 上传组件
        self.upload_widget = UploadWidget()
        left_layout.addWidget(self.upload_widget)
        
        # 图像画布容器
        self.image_canvas = ImageCanvasContainer()
        self.image_canvas.setMinimumSize(600, 400)
        left_layout.addWidget(self.image_canvas, 1)
        
        left_panel.setLayout(left_layout)
        
        # 右侧标签页（分析结果和历史记录）
        self.right_tabs = QTabWidget()
        self.right_tabs.setMaximumWidth(450)
        
        # 颜色分析标签页
        analysis_panel = QWidget()
        analysis_layout = QVBoxLayout()
        analysis_layout.setContentsMargins(10, 10, 10, 10)
        analysis_layout.setSpacing(10)
        
        # 显示选项
        options_frame = QWidget()
        options_frame.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(10, 8, 10, 8)
        
        self.show_markers_checkbox = QCheckBox("显示颜色标记")
        self.show_markers_checkbox.setChecked(True)
        self.show_markers_checkbox.toggled.connect(self.toggleColorMarkers)
        
        options_layout.addWidget(self.show_markers_checkbox)
        options_layout.addStretch()
        options_frame.setLayout(options_layout)
        
        analysis_layout.addWidget(options_frame)
        
        # 颜色列表
        self.color_list_widget = ColorListWidget()
        analysis_layout.addWidget(self.color_list_widget, 1)
        
        analysis_panel.setLayout(analysis_layout)
        self.right_tabs.addTab(analysis_panel, "颜色分析")
        
        # 历史记录标签页
        self.history_widget = HistoryWidget()
        self.right_tabs.addTab(self.history_widget, "历史记录")
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(self.right_tabs)
        main_splitter.setSizes([1000, 450])
        
        main_layout.addWidget(main_splitter)
        central_widget.setLayout(main_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QSplitter::handle {
                background-color: #ddd;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
            QTabWidget::pane {
                border: 2px solid #007ACC;
                border-radius: 4px;
                background-color: white;
                padding: 5px;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                color: #333;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #007ACC;
                color: white;
                border-color: #007ACC;
            }
            QTabBar::tab:hover:!selected {
                background-color: #f0f0f0;
                border-color: #007ACC;
            }
            QCheckBox {
                font-size: 12px;
                color: #333;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #ccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #007ACC;
                background-color: #007ACC;
                border-radius: 3px;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }
        """)
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 打开文件
        open_action = QAction("打开图片", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.upload_widget.select_file)
        file_menu.addAction(open_action)
        
        # 从剪贴板粘贴
        paste_action = QAction("从剪贴板粘贴", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.upload_widget.paste_from_clipboard)
        file_menu.addAction(paste_action)
        
        file_menu.addSeparator()
        
        # 导出调色板
        export_action = QAction("导出调色板", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_palette)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 切换到历史记录
        history_action = QAction("历史记录", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(lambda: self.right_tabs.setCurrentIndex(1))
        view_menu.addAction(history_action)
        
        # 切换到颜色分析
        analysis_action = QAction("颜色分析", self)
        analysis_action.setShortcut("Ctrl+A")
        analysis_action.triggered.connect(lambda: self.right_tabs.setCurrentIndex(0))
        view_menu.addAction(analysis_action)
        
        view_menu.addSeparator()
        
        # 切换颜色标记
        self.toggle_markers_action = QAction("显示颜色标记", self)
        self.toggle_markers_action.setCheckable(True)
        self.toggle_markers_action.setChecked(True)
        self.toggle_markers_action.triggered.connect(self.toggleColorMarkers)
        view_menu.addAction(self.toggle_markers_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        
        # 图片信息标签
        self.image_info_label = QLabel("")
        self.status_bar.addWidget(self.image_info_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        self.update_status("就绪")
    
    def setup_connections(self):
        """设置信号连接"""
        # 上传组件连接
        self.upload_widget.image_uploaded.connect(self.analyze_image)
        self.upload_widget.upload_error.connect(self.on_upload_error)
        
        # 图像画布连接
        self.image_canvas.colorClicked.connect(self.on_color_clicked)
        
        # 颜色列表连接
        self.color_list_widget.color_selected.connect(self.on_color_clicked)
        
        # 历史记录连接
        self.history_widget.recordSelected.connect(self.onHistoryRecordSelected)
    
    def on_upload_error(self, error_message: str):
        """处理上传错误"""
        self.update_status(f"上传失败: {error_message}")
    
    def analyze_image(self, file_path: str):
        """分析图片"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            return
        
        self.update_status("正在分析图片...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 创建分析线程
        self.analysis_thread = AnalysisThread(file_path)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_completed)
        self.analysis_thread.analysis_error.connect(self.on_analysis_failed)
        self.analysis_thread.start()
    
    def on_analysis_completed(self, image_info: ImageInfo):
        """分析完成处理"""
        try:
            self.current_image_info = image_info
            
            # 更新图像画布
            self.image_canvas.setImageInfo(image_info)
            
            # 更新颜色列表
            self.color_list_widget.set_colors(image_info.colors)
            
            # 添加到历史记录
            self.history_widget.addRecord(image_info)
            
            # 切换到分析结果标签页
            self.right_tabs.setCurrentIndex(0)
            
            # 更新状态栏
            color_count = len(image_info.colors)
            analysis_time = image_info.analysis_time
            self.update_status(f"分析完成：提取了 {color_count} 种颜色，耗时 {analysis_time:.2f} 秒")
            
            # 隐藏进度条
            self.progress_bar.hide()
            
        except Exception as e:
            self.on_analysis_failed(f"显示分析结果时出错: {str(e)}")
    
    def on_analysis_failed(self, error_message: str):
        """分析失败处理"""
        self.progress_bar.setVisible(False)
        self.update_status(f"分析失败: {error_message}")
        
        QMessageBox.critical(
            self,
            "分析失败",
            f"无法分析图片:\n{error_message}",
            QMessageBox.StandardButton.Ok
        )
    
    def on_color_clicked(self, hex_color: str):
        """处理颜色点击"""
        self.update_status(f"已复制颜色: {hex_color}")
    
    def onHistoryRecordSelected(self, record):
        """处理历史记录选择"""
        # 加载历史记录的图像信息
        self.current_image_info = record.image_info
        
        # 显示分析面板
        self.show_analysis_panel()
        
        # 更新UI
        self.image_canvas.setImageInfo(record.image_info)
        self.color_list_widget.set_colors(record.image_info.colors)
        
        # 更新状态
        color_count = len(record.image_info.colors)
        self.update_status(f"已加载历史记录: 包含 {color_count} 种颜色")
        
        # 更新图片信息
        file_size_mb = record.image_info.size_bytes / (1024 * 1024)
        info_text = f"{os.path.basename(record.image_info.file_path)} | {record.image_info.width}×{record.image_info.height} | {file_size_mb:.1f}MB"
        self.image_info_label.setText(info_text)
        
        # 切换到分析结果标签页
        self.right_tabs.setCurrentIndex(0)
    
    def show_analysis_panel(self):
        """显示分析面板"""
        self.right_tabs.setVisible(True)
    
    def hide_analysis_panel(self):
        """隐藏分析面板"""
        self.right_tabs.setVisible(False)
    
    def toggleColorMarkers(self, checked: bool = None):
        """切换颜色标记显示"""
        if checked is None:
            checked = self.show_markers_checkbox.isChecked()
        
        self.image_canvas.toggleColorMarkers(checked)
        self.show_markers_checkbox.setChecked(checked)
        self.toggle_markers_action.setChecked(checked)
    
    def clear_analysis(self):
        """清空分析结果"""
        self.current_image_info = None
        self.color_list_widget.clear_colors()
        self.image_canvas.setImageInfo(None)
        self.image_info_label.setText("")
        self.update_status("已清空分析结果")
        
        # 隐藏分析面板
        self.hide_analysis_panel()
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 qtPicColor",
            """
            <h3>qtPicColor - 图片颜色分析工具</h3>
            <p>版本: 1.0.0</p>
            <p>一个基于 PyQt6 的图片颜色分析工具，可以提取图片中的主要颜色。</p>
            <p>功能特性：</p>
            <ul>
                <li>支持多种图片格式</li>
                <li>智能颜色提取</li>
                <li>颜色标记显示</li>
                <li>历史记录管理</li>
                <li>一键复制颜色值</li>
            </ul>
            <p>© 2025 qtPicColor 开发团队</p>
            """
        )
    
    def update_status(self, message: str):
        """更新状态栏信息"""
        self.image_info_label.setText(message)
    
    def export_palette(self):
        """导出调色板"""
        if not self.current_image_info or not self.current_image_info.colors:
            QMessageBox.information(
                self,
                "提示",
                "请先分析图片以获取颜色信息",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # 这里可以添加导出功能的实现
        QMessageBox.information(
            self,
            "功能开发中",
            "导出调色板功能正在开发中",
            QMessageBox.StandardButton.Ok
        )
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import tempfile
            import glob
            
            temp_dir = tempfile.gettempdir()
            pattern = os.path.join(temp_dir, "qtpiccolor_*")
            
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        # 检查文件是否超过1小时未修改
                        import time
                        if time.time() - os.path.getmtime(file_path) > 3600:
                            os.remove(file_path)
                except Exception:
                    pass  # 忽略删除失败的文件
                    
        except Exception:
            pass  # 忽略清理过程中的错误
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止分析线程
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait(3000)  # 等待最多3秒
        
        # 停止定时器
        self.cleanup_timer.stop()
        
        # 清理临时文件
        self.cleanup_temp_files()
        
        event.accept() 