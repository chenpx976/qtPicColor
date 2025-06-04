# qtPicColor - 图片颜色分析工具

一个基于 PyQt6 的桌面应用程序，用于分析图片中的颜色分布，为设计师、开发者和艺术爱好者提供便捷的颜色提取和分析功能。

![qtPicColor Screenshot](docs/screenshot.png)

## ✨ 主要功能

- 🖼️ **多格式支持**：支持 PNG、JPG、JPEG、BMP、GIF、TIFF、WEBP 等常见图片格式
- 📤 **多种上传方式**：支持拖拽上传、点击选择文件、剪贴板粘贴（Ctrl+V）
- 🎨 **智能颜色分析**：使用 K-means 聚类算法提取图片中的主要颜色
- 📊 **可视化展示**：1024×1024 画布展示颜色分布，色块大小对应颜色占比
- 🌈 **多种颜色格式**：支持 HEX、RGB、HSL、HSV 格式显示和复制
- 📋 **一键复制**：点击任意颜色块或列表项即可复制颜色值到剪贴板
- ⚡ **高性能**：多线程处理，不阻塞 UI，支持大图片快速分析

## 🚀 快速开始

### 使用 uv 安装（推荐）

```bash
# 克隆项目
git clone https://github.com/qtpiccolor/qtpiccolor.git
cd qtpiccolor

# 使用 uv 安装依赖
uv sync

# 运行应用
uv run qtpiccolor
```

### 传统安装方式

```bash
# 克隆项目
git clone https://github.com/qtpiccolor/qtpiccolor.git
cd qtpiccolor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行应用
qtpiccolor
```

## 🎯 使用方法

1. **上传图片**：
   - 拖拽图片文件到上传区域
   - 点击"选择图片文件"按钮
   - 使用 Ctrl+V 粘贴剪贴板中的图片

2. **分析颜色**：
   - 应用会自动分析上传的图片
   - 等待分析完成（通常几秒钟）

3. **查看结果**：
   - 在画布中查看颜色分布图
   - 在右侧列表中查看详细颜色信息

4. **复制颜色**：
   - 点击画布中的颜色块复制 HEX 值
   - 点击列表中的颜色项复制当前格式的颜色值
   - 使用"复制所有颜色"按钮复制所有颜色

## 🛠️ 技术栈

- **UI 框架**：PyQt6
- **图像处理**：Pillow (PIL)
- **颜色分析**：scikit-learn (K-means 聚类)
- **数值计算**：NumPy
- **图像科学**：scikit-image
- **包管理**：uv

## 📝 开发

### 项目结构

```
qtPicColor/
├── src/
│   ├── qtpiccolor/
│   │   ├── __init__.py
│   │   ├── main.py              # 应用入口
│   │   ├── ui/                  # UI 组件
│   │   │   ├── main_window.py   # 主窗口
│   │   │   ├── upload_widget.py # 上传组件
│   │   │   ├── canvas_widget.py # 画布组件
│   │   │   └── color_list.py    # 颜色列表组件
│   │   ├── core/                # 核心功能
│   │   │   ├── models.py        # 数据模型
│   │   │   └── color_analyzer.py # 颜色分析器
│   │   └── utils/               # 工具函数
│   │       ├── file_handler.py  # 文件处理
│   │       └── clipboard.py     # 剪贴板操作
├── tests/                       # 测试文件
├── docs/                        # 文档
└── pyproject.toml              # 项目配置
```

### 开发环境设置

```bash
# 安装开发依赖
uv add --dev black flake8 pytest pytest-qt

# 代码格式化
uv run black src/

# 代码检查
uv run flake8 src/

# 运行测试
uv run pytest
```

## 🐛 问题反馈

如果您遇到任何问题或有改进建议，请在 [GitHub Issues](https://github.com/qtpiccolor/qtpiccolor/issues) 中反馈。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 优秀的 Python GUI 框架
- [scikit-learn](https://scikit-learn.org/) - 强大的机器学习库
- [Pillow](https://python-pillow.org/) - Python 图像处理库
- [uv](https://github.com/astral-sh/uv) - 快速的 Python 包管理器

---

Made with ❤️ by qtPicColor Team
