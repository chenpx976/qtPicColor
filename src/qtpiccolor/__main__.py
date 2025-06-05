"""
qtPicColor 应用程序入口点
支持通过 python -m qtpiccolor 运行
"""

import sys
import os
from pathlib import Path

# 确保能找到模块路径
if getattr(sys, "frozen", False):
    # PyInstaller 打包后的环境
    application_path = Path(sys.executable).parent

    # 设置Qt环境变量
    qt_plugins_path = application_path / "PyQt6" / "Qt6" / "plugins"
    if qt_plugins_path.exists():
        os.environ["QT_PLUGIN_PATH"] = str(qt_plugins_path)
        os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(qt_plugins_path / "platforms")

    # 禁用Qt调试输出
    os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"

    # 设置平台插件
    if sys.platform == "darwin":
        os.environ["QT_QPA_PLATFORM"] = "cocoa"
    elif sys.platform == "win32":
        os.environ["QT_QPA_PLATFORM"] = "windows"
else:
    # 开发环境
    application_path = Path(__file__).parent

# 添加到 Python 路径
sys.path.insert(0, str(application_path))

try:
    from main import main
except ImportError:
    # 如果直接导入失败，尝试从 qtpiccolor 包导入
    try:
        from qtpiccolor.main import main
    except ImportError:
        # 最后尝试相对导入
        from .main import main

if __name__ == "__main__":
    main()
