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

项目包含两个GitHub Actions工作流，使用官方的 `astral-sh/setup-uv` action 进行依赖管理：

1. **`build.yml`** - 完整构建和发布工作流
   - 触发条件：推送标签（`v*`）或手动触发
   - 功能：构建完整的安装包并发布到GitHub Releases
   - 特性：使用 uv 缓存加速构建，自动依赖管理

2. **`test-build.yml`** - 轻量级测试工作流
   - 触发条件：推送到main/develop分支或PR到main分支
   - 功能：代码检查、测试和构建配置验证
   - 特性：快速反馈，并行测试多个平台

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

**GitHub Actions 构建:**
- `qtPicColor-v1.0.0-macOS.dmg` - macOS DMG 安装包
- `qtPicColor-v1.0.0-Windows-Setup.exe` - Windows NSIS 安装程序
- `qtPicColor-v1.0.0-macOS-Portable.zip` - macOS 便携版
- `qtPicColor-v1.0.0-Windows-Portable.zip` - Windows 便携版

**本地构建产物:**
- `qtPicColor-v1.0.0-macOS.dmg` - macOS DMG 安装包（仅 macOS）
- `qtPicColor-v1.0.0-macOS-Portable.zip` - macOS 便携版（仅 macOS）
- `qtPicColor-v1.0.0-Windows-Portable.zip` - Windows 便携版（仅 Windows）
- `qtPicColor.app` - macOS 应用程序包（仅 macOS）
- `qtPicColor/` - Windows 应用程序目录（仅 Windows）

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
7. **macOS**: 创建 DMG 安装包和便携版 ZIP
8. **Windows**: 创建便携版 ZIP
9. 在 `dist/` 目录生成可执行文件和安装包
10. 显示生成文件的大小信息

**干运行模式**（`--dry-run`）：
- 验证项目结构和配置
- 检查依赖是否可用
- 验证PyInstaller配置文件语法
- **macOS**: 检查 DMG 创建工具可用性
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
- `create-dmg` (推荐，用于创建高质量 DMG 文件)
  ```bash
  brew install create-dmg
  ```
- `hdiutil` (系统自带，备用方案)

**DMG 创建说明:**
- 本地构建脚本会自动检测可用的 DMG 创建工具
- 优先使用 `create-dmg` 工具（如果已安装）
- 如果 `create-dmg` 不可用，自动使用 `hdiutil` 作为备用方案
- 两种方案都能创建功能完整的 DMG 安装包

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

7. **macOS 相对导入错误**
   - 问题：`ImportError: attempted relative import with no known parent package`
   - 解决：已修复 `__main__.py` 中的导入问题，使用绝对导入和路径处理

8. **macOS DMG 创建失败**
   - 问题：DMG 文件无法生成或为空
   - 解决：改进了 DMG 创建流程，添加了备用方案和验证步骤

9. **macOS 图标问题**
   - 问题：.icns 文件创建失败
   - 解决：改进了图标创建流程，使用标准的 iconset 结构

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

3. **测试应用程序导入**：
   ```bash
   python test_app.py
   ```

4. **启用调试模式**：
   ```bash
   pyinstaller qtpiccolor.spec --clean --noconfirm --debug=all
   ```

5. **检查构建日志**：
   查看 PyInstaller 的详细输出

6. **测试导入**：
   ```python
   # 测试所有依赖是否可以正常导入
   import PyQt6.QtWidgets
   import PIL
   import numpy
   import sklearn
   import skimage
   ```

7. **macOS 特定调试**：
   ```bash
   # 检查 App Bundle 结构
   ls -la dist/qtPicColor.app/Contents/
   
   # 检查可执行文件
   file dist/qtPicColor.app/Contents/MacOS/qtPicColor
   
   # 检查依赖
   otool -L dist/qtPicColor.app/Contents/MacOS/qtPicColor
   
   # 手动测试启动
   dist/qtPicColor.app/Contents/MacOS/qtPicColor
   ```

### 已修复的问题

**v1.0.2 修复内容**：

1. **修复 macOS Qt 框架路径问题**
   - 问题：`EXC_BAD_ACCESS (SIGSEGV)` 在 `QLibraryInfoPrivate::paths` 函数中
   - 原因：PyInstaller 手动处理 Qt 框架时出现符号链接冲突
   - 解决：简化 PyInstaller 配置，让其自动处理 Qt 依赖
   - 在 `__main__.py` 中添加 Qt 环境变量设置

2. **改进 Qt 环境配置**
   - 在应用启动前设置 `QT_PLUGIN_PATH` 和 `QT_QPA_PLATFORM_PLUGIN_PATH`
   - 禁用 Qt 调试输出以减少日志噪音
   - 确保正确的平台插件加载（macOS: cocoa, Windows: windows）

3. **简化构建配置**
   - 移除手动 Qt 框架和插件处理
   - 让 PyInstaller 的内置 Qt 钩子自动处理依赖
   - 减少构建复杂性和潜在错误

**v1.0.1 修复内容**：

1. **修复 macOS 相对导入错误**
   - 更新 `__main__.py` 使用绝对导入
   - 添加路径处理逻辑支持 PyInstaller 环境
   - 改进模块查找机制

2. **修复 macOS DMG 创建问题**
   - 改进 DMG 创建流程
   - 添加 hdiutil 备用方案
   - 增加 DMG 内容验证
   - 改进错误处理和日志输出

3. **改进 macOS 图标处理**
   - 使用标准 iconset 结构
   - 创建完整的分辨率系列
   - 改进 .icns 文件生成
   - 添加图标验证步骤

4. **增强构建配置**
   - 添加更多隐式导入
   - 排除不必要的模块减小体积
   - 改进 App Bundle 元数据
   - 添加高分辨率支持

5. **添加构建测试**
   - 创建应用程序启动测试
   - 验证构建产物完整性
   - 添加自动化测试步骤

### 构建状态

**当前状态**：✅ **完全正常**

- ✅ macOS 应用程序可以正常启动
- ✅ Qt 界面正确显示
- ✅ 双击启动功能正常
- ✅ 命令行启动功能正常
- ✅ 便携版 ZIP 创建成功
- ✅ 版本号正确集成
- ✅ 图标文件正确显示

**测试结果**：
```bash
# 命令行测试
./dist/qtPicColor.app/Contents/MacOS/qtPicColor --help
# 输出：应用程序正常启动和退出

# 双击测试
open dist/qtPicColor.app
# 结果：应用程序正常启动，GUI 界面显示正常
```

**构建产物**：
- `qtPicColor.app` - macOS 应用程序包
- `qtPicColor-v1.0.0-macOS-Portable.zip` - 便携版压缩包（214MB）

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
- **现代依赖管理**: 使用官方 `astral-sh/setup-uv@v5` action
- **智能缓存**: 基于 `uv.lock` 的依赖缓存，显著加速构建
- **多平台构建**: 同时在 macOS 和 Windows 上构建
- **版本号集成**: 自动读取版本号并应用到构建产物
- **自动发布**: 标签推送时自动创建 GitHub Release
- **构建产物**: 自动上传带版本号的构建结果

**测试工作流** (`test-build.yml`)：
- **快速设置**: 使用 uv 快速安装和管理依赖
- **代码质量检查**: 运行 flake8 和 black 检查
- **单元测试**: 运行 pytest 测试套件
- **导入测试**: 验证模块可以正常导入
- **构建配置验证**: 使用干运行模式验证构建配置
- **多平台测试**: 在 Ubuntu、macOS 和 Windows 上并行测试

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