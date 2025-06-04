# qtPicColor 构建指南

本文档说明如何构建 qtPicColor 的 macOS 和 Windows 安装包。

## 自动构建 (GitHub Actions)

### 触发构建

GitHub Actions 工作流会在以下情况下自动触发：

1. **推送标签**: 当你推送以 `v` 开头的标签时（如 `v1.0.0`）
2. **Pull Request**: 向 `main` 分支提交 PR 时
3. **手动触发**: 在 GitHub 仓库的 Actions 页面手动运行

### 发布新版本

要发布新版本并自动构建安装包：

```bash
# 1. 更新版本号（在 pyproject.toml 中）
# 2. 提交更改
git add .
git commit -m "Release v1.0.0"

# 3. 创建并推送标签
git tag v1.0.0
git push origin v1.0.0
```

### 构建产物

GitHub Actions 会生成以下文件：

**macOS:**
- `qtPicColor-macOS.dmg` - DMG 安装包
- `qtPicColor-macOS-Portable.zip` - 便携版

**Windows:**
- `qtPicColor-Windows-Setup.exe` - NSIS 安装程序
- `qtPicColor-Windows-Portable.zip` - 便携版

## 本地构建

### 前提条件

1. **Python 3.8+** 已安装
2. **项目依赖** 已安装：
   ```bash
   pip install uv
   uv sync --dev
   ```

### 使用本地构建脚本

```bash
# 在项目根目录运行
python build_local.py
```

这个脚本会：
1. 自动创建图标文件（如果不存在）
2. 生成 PyInstaller 配置文件
3. 安装 PyInstaller（如果需要）
4. 执行构建过程
5. 在 `dist/` 目录生成可执行文件

### 手动构建

如果你想手动控制构建过程：

```bash
# 1. 安装 PyInstaller
pip install pyinstaller

# 2. 创建图标文件（可选）
# 将你的图标文件放在 src/qtpiccolor/resources/ 目录下
# - Windows: icon.ico
# - macOS: icon.icns

# 3. 运行 PyInstaller
pyinstaller qtpiccolor.spec --clean --noconfirm
```

## 平台特定说明

### macOS

**额外依赖:**
- `create-dmg` (用于创建 DMG 文件)
  ```bash
  brew install create-dmg
  ```

**代码签名:**
如果需要分发应用，建议进行代码签名：
```bash
# 签名应用
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/qtPicColor.app

# 公证应用（需要 Apple Developer 账户）
xcrun notarytool submit dist/qtPicColor-macOS.dmg --keychain-profile "notarytool-profile" --wait
```

### Windows

**额外依赖:**
- `NSIS` (用于创建安装程序)
  ```bash
  # 使用 Chocolatey 安装
  choco install nsis
  ```

**代码签名:**
如果有代码签名证书，可以签名可执行文件：
```bash
# 使用 signtool 签名
signtool sign /f certificate.p12 /p password /t http://timestamp.digicert.com dist/qtPicColor.exe
```

## 故障排除

### 常见问题

1. **缺少依赖模块**
   - 在 `qtpiccolor.spec` 的 `hiddenimports` 中添加缺失的模块

2. **资源文件未包含**
   - 检查 `datas` 配置，确保所有资源文件都被包含

3. **图标文件问题**
   - 确保图标文件格式正确（Windows: .ico, macOS: .icns）
   - 图标文件路径正确

4. **应用无法启动**
   - 检查控制台输出的错误信息
   - 尝试在命令行运行可执行文件查看详细错误

### 调试构建

如果构建失败，可以：

1. **启用调试模式**：
   ```bash
   pyinstaller qtpiccolor.spec --clean --noconfirm --debug=all
   ```

2. **检查构建日志**：
   查看 PyInstaller 的详细输出

3. **测试导入**：
   ```python
   # 测试所有依赖是否可以正常导入
   import PyQt6.QtWidgets
   import PIL
   import numpy
   import sklearn
   import skimage
   ```

## 自定义构建

### 修改应用图标

1. 准备图标文件：
   - **Windows**: 创建 `.ico` 文件（推荐 256x256 像素）
   - **macOS**: 创建 `.icns` 文件或使用 `iconutil` 转换

2. 将图标文件放在 `src/qtpiccolor/resources/` 目录下

3. 更新 `qtpiccolor.spec` 中的图标路径

### 添加额外文件

在 `qtpiccolor.spec` 的 `datas` 部分添加：
```python
datas=[
    ('src/qtpiccolor/resources', 'qtpiccolor/resources'),
    ('path/to/extra/file', 'destination/path'),
],
```

### 优化构建大小

1. **排除不需要的模块**：
   ```python
   excludes=['tkinter', 'matplotlib', 'scipy.tests'],
   ```

2. **使用 UPX 压缩**：
   ```python
   upx=True,
   upx_exclude=[],
   ```

3. **单文件模式**（可选）：
   修改 `EXE` 配置为 `onefile=True`

## 持续集成

GitHub Actions 工作流包含以下特性：

- **多平台构建**: 同时在 macOS 和 Windows 上构建
- **自动发布**: 标签推送时自动创建 GitHub Release
- **构建缓存**: 缓存依赖以加速构建
- **构建产物**: 自动上传构建结果

要自定义工作流，编辑 `.github/workflows/build.yml` 文件。 