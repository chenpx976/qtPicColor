#!/usr/bin/env python3
"""
qtPicColor 主程序
"""

import sys
import os
import logging
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QFileDialog,
    QScrollArea,
    QFrame,
    QSizePolicy,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont

from .ui.main_window import MainWindow


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("启动 qtPicColor 应用程序")

    # 创建应用程序
    app = QApplication(sys.argv)

    # 设置应用程序属性
    app.setApplicationName("qtPicColor")
    app.setApplicationDisplayName("qtPicColor - 图片颜色分析工具")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("qtPicColor Team")

    # 设置应用程序样式
    app.setStyle("Fusion")  # 使用 Fusion 样式，在所有平台上保持一致

    try:
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()

        logger.info("应用程序界面已显示")

        # 运行应用程序
        exit_code = app.exec()
        logger.info(f"应用程序退出，退出码: {exit_code}")

        return exit_code

    except Exception as e:
        logger.error(f"应用程序运行时发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
