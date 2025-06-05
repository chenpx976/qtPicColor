# qtPicColor 构建指南

本文档说明如何构建 qtPicColor 的 macOS 和 Windows 安装包。

## 版本管理

项目版本号在 `pyproject.toml` 文件中定义：

```toml
[project]
version = "1.0.0"
```

构建系统会自动从此文件读取版本号，并将其包含在：
- 构建产物文件名中
- 应用程序版本信息中
- 安装包元数据中
- GitHub Release 标题中

## 自动构建 (GitHub Actions)

### 工作流说明

项目包含两个GitHub Actions工作流：

1. **`build.yml`** - 完整构建和发布工作流
   - 触发条件：推送标签（`v*`）或手动触发
   - 功能：构建完整的安装包并发布到GitHub Releases

2. **`test-build.yml`** - 轻量级测试工作流
   - 触发条件：推送到main/develop分支或PR到main分支
   - 功能：代码检查、测试和构建配置验证

### 触发构建

**完整构建**会在以下情况下自动触发：

1. **推送标签**: 当你推送以 `v` 开头的标签时（如 `v1.0.0`）
2. **手动触发**: 在 GitHub 仓库的 Actions 页面手动运行

**测试构建**会在以下情况下自动触发：

1. **推送代码**: 向 `main` 或 `develop` 分支推送代码
2. **Pull Request**: 向 `main` 分支提交 PR 时

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

GitHub Actions 会生成以下带版本号的文件：

**macOS:**
- `qtPicColor-v{version}-macOS.dmg` - DMG 安装包
- `qtPicColor-v{version}-macOS-Portable.zip` - 便携版

**Windows:**
- `qtPicColor-v{version}-Windows-Setup.exe` - NSIS 安装程序
- `qtPicColor-v{version}-Windows-Portable.zip` - 便携版

例如，版本 1.0.0 的构建产物：
- `qtPicColor-v1.0.0-macOS.dmg`
- `qtPicColor-v1.0.0-Windows-Setup.exe`
- `qtPicColor-v1.0.0-macOS-Portable.zip`
- `qtPicColor-v1.0.0-Windows-Portable.zip`

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
# 完整构建（包含版本号）
python build_local.py

# 验证构建配置（不实际构建）
python build_local.py --dry-run

# 查看当前版本号
python get_version.py
```

构建脚本功能：
1. 自动从 `pyproject.toml` 读取版本号
2. 创建图标文件（如果不存在）
3. 生成带版本信息的 PyInstaller 配置文件
4. 创建 Windows 版本信息文件
5. 安装 PyInstaller（如果需要）
6. 执行构建过程
7. 生成带版本号的便携版压缩包
8. 在 `dist/` 目录生成可执行文件

**干运行模式**（`--dry-run`）：
- 验证项目结构和配置
- 检查依赖是否可用
- 验证PyInstaller配置文件语法
- 不执行实际构建，适合CI/CD测试

### 版本信息集成

构建系统会将版本信息集成到应用程序中：

**Windows:**
- 可执行文件包含完整的版本信息资源
- 在文件属性中显示版本号、公司信息等
- 安装程序显示版本号

**macOS:**
- App Bundle 包含版本信息
- 在"关于"对话框中显示版本号
- DMG 卷标包含版本号

### 手动构建

如果你想手动控制构建过程：

```bash
# 1. 获取版本号
VERSION=$(python get_version.py)
echo "构建版本: $VERSION"

# 2. 安装 PyInstaller
pip install pyinstaller

# 3. 创建图标文件（可选）
# 将你的图标文件放在 src/qtpiccolor/resources/ 目录下
# - Windows: icon.ico
# - macOS: icon.icns

# 4. 运行 PyInstaller
pyinstaller qtpiccolor.spec --clean --noconfirm
```

## 平台特定说明

### macOS

**额外依赖:**
- `create-dmg` (用于创建 DMG 文件)
  ```bash
  brew install create-dmg
  ```

**版本信息:**
- DMG 卷标显示版本号：`qtPicColor v1.0.0`
- App Bundle 包含 `CFBundleShortVersionString` 和 `CFBundleVersion`
- 支持图片文件关联

**代码签名:**
如果需要分发应用，建议进行代码签名：
```bash
# 签名应用
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/qtPicColor.app

# 公证应用（需要 Apple Developer 账户）
xcrun notarytool submit dist/qtPicColor-v1.0.0-macOS.dmg --keychain-profile "notarytool-profile" --wait
```

### Windows

**额外依赖:**
- `NSIS` (用于创建安装程序)
  ```bash
  # 使用 Chocolatey 安装
  choco install nsis
  ```

**版本信息:**
- 可执行文件包含完整的版本信息资源
- 安装程序标题显示版本号：`qtPicColor v1.0.0`
- 注册表中记录版本信息
- 控制面板"程序和功能"中显示版本号

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

5. **GitHub Actions失败**
   - 检查Actions日志中的具体错误信息
   - 确保所有依赖都在 `pyproject.toml` 中正确声明
   - 验证Python版本兼容性

6. **版本号问题**
   - 确保 `pyproject.toml` 中的版本号格式正确
   - 版本号应遵循语义化版本规范（如 `1.0.0`）
   - 检查 `get_version.py` 脚本是否能正确读取版本号

### 调试构建

如果构建失败，可以：

1. **使用干运行模式验证配置**：
   ```bash
   python build_local.py --dry-run
   ```

2. **检查版本号**：
   ```bash
   python get_version.py
   ```

3. **启用调试模式**：
   ```bash
   pyinstaller qtpiccolor.spec --clean --noconfirm --debug=all
   ```

4. **检查构建日志**：
   查看 PyInstaller 的详细输出

5. **测试导入**：
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

### GitHub Actions 特性

**完整构建工作流** (`build.yml`)：
- **多平台构建**: 同时在 macOS 和 Windows 上构建
- **版本号集成**: 自动读取版本号并应用到构建产物
- **自动发布**: 标签推送时自动创建 GitHub Release
- **构建缓存**: 缓存依赖以加速构建
- **构建产物**: 自动上传带版本号的构建结果

**测试工作流** (`test-build.yml`)：
- **代码质量检查**: 运行 flake8 和 black 检查
- **单元测试**: 运行 pytest 测试套件
- **导入测试**: 验证模块可以正常导入
- **构建配置验证**: 使用干运行模式验证构建配置

### 自定义工作流

要自定义工作流，编辑相应的文件：
- `.github/workflows/build.yml` - 完整构建工作流
- `.github/workflows/test-build.yml` - 测试工作流

### 最佳实践

1. **分离关注点**: 使用不同的工作流处理测试和发布
2. **快速反馈**: 测试工作流提供快速的代码质量反馈
3. **安全发布**: 只有标签推送才触发完整构建和发布
4. **版本管理**: 使用语义化版本标签（如 `v1.0.0`）
5. **版本一致性**: 确保标签版本与 `pyproject.toml` 中的版本一致 