"""主窗口"""

import os
import time
from typing import Optional
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QMenuBar, QStatusBar, QMessageBox, 
                             QProgressBar, QLabel, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence

from .upload_widget import UploadWidget
from .canvas_widget import CanvasWidget
from .color_list import ColorListWidget
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
        
        # 左侧分割器（上传区域和画布）
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # 上传组件
        self.upload_widget = UploadWidget()
        left_splitter.addWidget(self.upload_widget)
        
        # 画布组件（使用滚动区域）
        self.canvas_widget = CanvasWidget()
        canvas_scroll = QScrollArea()
        canvas_scroll.setWidget(self.canvas_widget)
        canvas_scroll.setWidgetResizable(True)
        canvas_scroll.setMinimumSize(600, 400)
        left_splitter.addWidget(canvas_scroll)
        
        # 设置分割比例
        left_splitter.setSizes([300, 700])
        
        # 右侧颜色列表
        self.color_list_widget = ColorListWidget()
        self.color_list_widget.setMaximumWidth(400)
        
        # 主分割器
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_splitter)
        main_splitter.addWidget(self.color_list_widget)
        main_splitter.setSizes([1000, 400])
        
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
        """)
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        # 打开文件
        open_action = QAction("打开图片(&O)", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("打开图片文件")
        open_action.triggered.connect(self.upload_widget.select_file)
        file_menu.addAction(open_action)
        
        # 粘贴
        paste_action = QAction("粘贴图片(&V)", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.setStatusTip("从剪贴板粘贴图片")
        paste_action.triggered.connect(self.upload_widget.paste_from_clipboard)
        file_menu.addAction(paste_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("退出应用程序")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        # 复制所有颜色
        copy_all_action = QAction("复制所有颜色(&A)", self)
        copy_all_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
        copy_all_action.setStatusTip("复制所有颜色值到剪贴板")
        copy_all_action.triggered.connect(self.color_list_widget.copy_all_colors)
        edit_menu.addAction(copy_all_action)
        
        # 清空
        clear_action = QAction("清空分析结果(&C)", self)
        clear_action.setShortcut(QKeySequence("Ctrl+Shift+X"))
        clear_action.setStatusTip("清空当前分析结果")
        clear_action.triggered.connect(self.clear_analysis)
        edit_menu.addAction(clear_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        # 关于
        about_action = QAction("关于 qtPicColor(&A)", self)
        about_action.setStatusTip("关于此应用程序")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 图片信息标签
        self.image_info_label = QLabel("")
        self.status_bar.addPermanentWidget(self.image_info_label)
    
    def setup_connections(self):
        """设置信号连接"""
        # 上传组件信号
        self.upload_widget.image_uploaded.connect(self.on_image_uploaded)
        self.upload_widget.upload_error.connect(self.on_upload_error)
        
        # 画布组件信号
        self.canvas_widget.color_clicked.connect(self.on_color_clicked)
        
        # 颜色列表组件信号
        self.color_list_widget.color_selected.connect(self.on_color_selected)
    
    def on_image_uploaded(self, file_path: str):
        """处理图片上传"""
        self.start_analysis(file_path)
    
    def on_upload_error(self, error_message: str):
        """处理上传错误"""
        self.update_status(f"上传失败: {error_message}")
        QMessageBox.critical(self, "上传错误", error_message)
    
    def start_analysis(self, image_path: str):
        """开始颜色分析"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait()
        
        self.update_status("正在分析图片颜色...")
        self.show_progress(True)
        
        # 创建分析线程
        self.analysis_thread = AnalysisThread(image_path, max_colors=16)
        self.analysis_thread.analysis_finished.connect(self.on_analysis_finished)
        self.analysis_thread.analysis_error.connect(self.on_analysis_error)
        self.analysis_thread.start()
    
    def on_analysis_finished(self, image_info: ImageInfo):
        """分析完成处理"""
        self.current_image_info = image_info
        
        # 更新UI
        self.canvas_widget.set_colors(image_info.colors)
        self.color_list_widget.set_colors(image_info.colors)
        
        # 更新状态
        self.show_progress(False)
        color_count = len(image_info.colors)
        analysis_time = image_info.analysis_time
        self.update_status(f"分析完成: 提取了 {color_count} 种颜色 (用时 {analysis_time:.2f}s)")
        
        # 更新图片信息
        file_size_mb = image_info.size_bytes / (1024 * 1024)
        info_text = f"{os.path.basename(image_info.file_path)} | {image_info.width}×{image_info.height} | {file_size_mb:.1f}MB"
        self.image_info_label.setText(info_text)
    
    def on_analysis_error(self, error_message: str):
        """分析错误处理"""
        self.show_progress(False)
        self.update_status(f"分析失败: {error_message}")
        QMessageBox.critical(self, "分析错误", f"颜色分析失败:\n{error_message}")
    
    def on_color_clicked(self, hex_color: str):
        """画布颜色点击处理"""
        self.update_status(f"已复制颜色: {hex_color}")
    
    def on_color_selected(self, color_value: str):
        """颜色列表选择处理"""
        self.update_status(f"已复制颜色: {color_value}")
    
    def clear_analysis(self):
        """清空分析结果"""
        if self.current_image_info:
            reply = QMessageBox.question(
                self, 
                "确认清空", 
                "确定要清空当前的分析结果吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.current_image_info = None
                self.canvas_widget.set_colors([])
                self.color_list_widget.set_colors([])
                self.update_status("已清空分析结果")
                self.image_info_label.setText("")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
<h3>qtPicColor 图片颜色分析工具</h3>
<p>版本: 1.0.0</p>
<p>一个基于 PyQt6 的桌面应用程序，用于分析图片中的颜色分布。</p>

<h4>主要功能：</h4>
<ul>
<li>支持多种图片格式（PNG、JPG、JPEG、BMP、GIF等）</li>
<li>拖拽或粘贴上传图片</li>
<li>智能颜色分析和提取</li>
<li>可视化颜色分布展示</li>
<li>支持多种颜色格式（HEX、RGB、HSL、HSV）</li>
<li>一键复制颜色值</li>
</ul>

<h4>使用方法：</h4>
<ol>
<li>拖拽图片到上传区域或点击选择文件</li>
<li>等待系统自动分析颜色</li>
<li>查看颜色分布图和颜色列表</li>
<li>点击任意颜色块或列表项复制颜色值</li>
</ol>

<p>技术栈: Python, PyQt6, scikit-learn, Pillow</p>
        """
        QMessageBox.about(self, "关于 qtPicColor", about_text)
    
    def update_status(self, message: str):
        """更新状态栏消息"""
        self.status_label.setText(message)
    
    def show_progress(self, show: bool):
        """显示/隐藏进度条"""
        self.progress_bar.setVisible(show)
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        import tempfile
        import glob
        
        temp_dir = tempfile.gettempdir()
        pattern = os.path.join(temp_dir, "tmp*.png")
        
        for temp_file in glob.glob(pattern):
            try:
                # 只删除超过1小时的临时文件
                if os.path.getmtime(temp_file) < time.time() - 3600:
                    os.unlink(temp_file)
            except:
                pass  # 忽略删除失败的情况
    
    def closeEvent(self, event):
        """关闭事件处理"""
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.quit()
            self.analysis_thread.wait(3000)  # 等待最多3秒
        
        # 清理临时文件
        self.cleanup_temp_files()
        event.accept() 