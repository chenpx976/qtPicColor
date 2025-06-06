#!/usr/bin/env python3
"""
本地构建脚本 - 用于测试PyInstaller打包
"""

import os
import sys
import shutil
import subprocess
import argparse
import re
from pathlib import Path

def get_version():
    """从 pyproject.toml 中获取版本号"""
    try:
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            raise FileNotFoundError("找不到 pyproject.toml 文件")
        
        # 读取文件内容
        content = pyproject_path.read_text(encoding='utf-8')
        
        # 使用正则表达式提取版本号
        version_match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
        if not version_match:
            raise ValueError("在 pyproject.toml 中找不到版本号")
        
        return version_match.group(1)
    
    except Exception as e:
        print(f"错误: 无法获取版本号 - {e}", file=sys.stderr)
        return None

def run_command(cmd, cwd=None, dry_run=False):
    """运行命令并检查结果"""
    if dry_run:
        print(f"(干运行模式) 将执行命令: {cmd}")
        # 对于某些检查命令，在干运行模式下也要实际执行
        if cmd.startswith("which "):
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
            return result.returncode == 0
        return True
    
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    if result.stdout.strip():
        print(f"命令输出: {result.stdout.strip()}")
    return True

def create_icon(dry_run=False):
    """创建默认图标文件"""
    if dry_run:
        print("(干运行模式) 跳过图标文件创建")
        return True
        
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 确保资源目录存在
        resources_dir = Path("src/qtpiccolor/resources")
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建一个更好看的图标
        img = Image.new('RGBA', (512, 512), (70, 130, 180, 255))
        draw = ImageDraw.Draw(img)
        
        # 绘制圆形背景
        draw.ellipse([50, 50, 462, 462], fill=(255, 255, 255, 255))
        draw.ellipse([60, 60, 452, 452], fill=(70, 130, 180, 255))
        
        # 绘制文字
        try:
            # 尝试使用系统字体
            font = ImageFont.truetype("Arial", 120)
        except:
            # 如果没有找到字体，使用默认字体
            font = ImageFont.load_default()
        
        # 计算文字位置
        text = "QPC"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (512 - text_width) // 2
        y = (512 - text_height) // 2 - 20
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # 保存为不同格式
        if sys.platform == 'win32':
            # Windows: 创建 ICO 文件
            img.save('src/qtpiccolor/resources/icon.ico', format='ICO', 
                    sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print("Windows图标文件创建成功: icon.ico")
        else:
            # macOS: 创建 ICNS 文件
            img.save('src/qtpiccolor/resources/icon.png')
            
            if sys.platform == 'darwin':
                # 创建iconset目录
                iconset_dir = Path("src/qtpiccolor/resources/icon.iconset")
                if iconset_dir.exists():
                    shutil.rmtree(iconset_dir)
                iconset_dir.mkdir(exist_ok=True)
                
                # 创建不同尺寸的图标
                icon_sizes = [
                    (16, 'icon_16x16.png'),
                    (32, 'icon_16x16@2x.png'),
                    (32, 'icon_32x32.png'),
                    (64, 'icon_32x32@2x.png'),
                    (128, 'icon_128x128.png'),
                    (256, 'icon_128x128@2x.png'),
                    (256, 'icon_256x256.png'),
                    (512, 'icon_256x256@2x.png'),
                    (512, 'icon_512x512.png'),
                    (1024, 'icon_512x512@2x.png'),
                ]
                
                for size, filename in icon_sizes:
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    resized.save(iconset_dir / filename)
                
                # 使用iconutil创建.icns文件
                icns_path = Path("src/qtpiccolor/resources/icon.icns")
                if icns_path.exists():
                    icns_path.unlink()
                
                result = run_command(f"iconutil -c icns {iconset_dir} -o {icns_path}")
                if result and icns_path.exists():
                    print("macOS图标文件创建成功: icon.icns")
                    # 清理临时文件
                    shutil.rmtree(iconset_dir)
                else:
                    print("警告: iconutil命令失败，使用PNG作为备用图标")
            else:
                print("Linux图标文件创建成功: icon.png")
                
        return True
    except ImportError:
        print("警告: PIL未安装，无法创建图标文件")
        return False
    except Exception as e:
        print(f"创建图标文件时出错: {e}")
        return False

def create_version_info_file(version, dry_run=False):
    """创建Windows版本信息文件"""
    if sys.platform != 'win32':
        return True
        
    if dry_run:
        print("(干运行模式) 跳过Windows版本信息文件创建")
        return True
    
    try:
        # 解析版本号
        version_parts = version.split('.')
        major = version_parts[0] if len(version_parts) > 0 else "0"
        minor = version_parts[1] if len(version_parts) > 1 else "0"
        patch = version_parts[2] if len(version_parts) > 2 else "0"
        build = version_parts[3] if len(version_parts) > 3 else "0"
        
        version_info_content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, {build}),
    prodvers=({major}, {minor}, {patch}, {build}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'qtPicColor Team'),
           StringStruct(u'FileDescription', u'图片颜色分析工具'),
           StringStruct(u'FileVersion', u'{version}'),
           StringStruct(u'InternalName', u'qtPicColor'),
           StringStruct(u'LegalCopyright', u'Copyright © 2024 qtPicColor Team'),
           StringStruct(u'OriginalFilename', u'qtPicColor.exe'),
           StringStruct(u'ProductName', u'qtPicColor'),
           StringStruct(u'ProductVersion', u'{version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        with open('version_info.txt', 'w', encoding='utf-8') as f:
            f.write(version_info_content)
        
        print("Windows版本信息文件创建成功")
        return True
    except Exception as e:
        print(f"创建Windows版本信息文件时出错: {e}")
        return False

def create_spec_file(version, dry_run=False):
    """创建PyInstaller spec文件"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path

block_cipher = None

# 获取源码路径
src_path = Path('src')

a = Analysis(
    ['src/qtpiccolor/__main__.py'],
    pathex=[str(src_path), str(src_path / 'qtpiccolor')],
    binaries=[],
    datas=[
        ('src/qtpiccolor/resources', 'qtpiccolor/resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'numpy',
        'sklearn',
        'skimage',
        'qtpiccolor',
        'qtpiccolor.main',
        'qtpiccolor.ui',
        'qtpiccolor.core',
        'qtpiccolor.utils',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy.tests',
        'numpy.tests',
        'sklearn.tests',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='qtPicColor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/qtpiccolor/resources/icon.ico' if sys.platform == 'win32' else 'src/qtpiccolor/resources/icon.icns',
    version='version_info.txt' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='qtPicColor',
)

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='qtPicColor.app',
        icon='src/qtpiccolor/resources/icon.icns',
        bundle_identifier='com.qtpiccolor.app',
        info_plist={{
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '{version}',
            'CFBundleVersion': '{version}',
            'CFBundleDisplayName': 'qtPicColor',
            'CFBundleName': 'qtPicColor',
            'CFBundleExecutable': 'qtPicColor',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'LSMinimumSystemVersion': '10.15.0',
            'NSRequiresAquaSystemAppearance': False,
            'CFBundleDocumentTypes': [
                {{
                    'CFBundleTypeName': 'Image',
                    'CFBundleTypeRole': 'Viewer',
                    'LSItemContentTypes': ['public.image', 'public.jpeg', 'public.png'],
                    'CFBundleTypeExtensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'],
                }}
            ]
        }},
    )
'''
    
    if dry_run:
        print("(干运行模式) 跳过spec文件创建，但验证内容格式")
        # 验证spec文件内容是否有效
        try:
            compile(spec_content, 'qtpiccolor.spec', 'exec')
            print("✓ PyInstaller spec文件内容验证通过")
        except SyntaxError as e:
            print(f"✗ PyInstaller spec文件语法错误: {e}")
            return False
        return True
    
    with open('qtpiccolor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("PyInstaller spec文件创建成功")
    return True

def create_dmg(version, dry_run=False):
    """创建macOS DMG安装包"""
    if sys.platform != 'darwin':
        return True
        
    if dry_run:
        print("(干运行模式) 跳过DMG创建")
        return True
    
    try:
        # 验证App是否构建成功
        app_path = Path("dist/qtPicColor.app")
        if not app_path.exists():
            print("✗ qtPicColor.app 不存在，无法创建DMG")
            return False
        
        print("✓ 找到 qtPicColor.app，开始创建DMG...")
        
        # 创建DMG临时目录
        dmg_dir = Path("dist/dmg")
        if dmg_dir.exists():
            shutil.rmtree(dmg_dir)
        dmg_dir.mkdir(exist_ok=True)
        
        # 复制应用到DMG目录
        shutil.copytree(app_path, dmg_dir / "qtPicColor.app")
        
        # 创建Applications文件夹的符号链接
        applications_link = dmg_dir / "Applications"
        if applications_link.exists():
            applications_link.unlink()
        applications_link.symlink_to("/Applications")
        
        # 设置DMG文件名
        dmg_name = f"qtPicColor-v{version}-macOS.dmg"
        dmg_path = Path("dist") / dmg_name
        
        # 删除可能存在的旧DMG文件
        if dmg_path.exists():
            dmg_path.unlink()
        
        print(f"创建DMG: {dmg_name}")
        
        # 检查是否有create-dmg工具
        create_dmg_available = run_command("which create-dmg", dry_run=True)
        
        if create_dmg_available:
            # 使用create-dmg工具
            icon_path = Path("src/qtpiccolor/resources/icon.icns")
            icon_arg = f'--volicon "{icon_path}"' if icon_path.exists() else ""
            
            cmd = f'''create-dmg \\
              --volname "qtPicColor v{version}" \\
              {icon_arg} \\
              --window-pos 200 120 \\
              --window-size 800 400 \\
              --icon-size 100 \\
              --icon "qtPicColor.app" 200 190 \\
              --hide-extension "qtPicColor.app" \\
              --app-drop-link 600 185 \\
              --no-internet-enable \\
              "{dmg_path}" \\
              "{dmg_dir}/"'''
            
            if run_command(cmd):
                print(f"✓ DMG创建成功: {dmg_path}")
            else:
                print("create-dmg失败，尝试备用方案...")
                return create_dmg_fallback(version, dmg_dir, dmg_path)
        else:
            print("create-dmg不可用，使用hdiutil创建DMG...")
            return create_dmg_fallback(version, dmg_dir, dmg_path)
        
        # 验证DMG文件
        if dmg_path.exists() and dmg_path.stat().st_size > 0:
            print(f"✓ DMG文件验证成功: {dmg_path} ({dmg_path.stat().st_size / 1024 / 1024:.1f} MB)")
            # 清理临时文件
            shutil.rmtree(dmg_dir)
            return True
        else:
            print("✗ DMG文件创建失败或为空")
            return False
            
    except Exception as e:
        print(f"创建DMG时出错: {e}")
        return False

def create_dmg_fallback(version, dmg_dir, dmg_path):
    """使用hdiutil创建DMG的备用方案"""
    try:
        # 创建临时DMG
        temp_dmg = Path("dist/temp.dmg")
        if temp_dmg.exists():
            temp_dmg.unlink()
        
        cmd = f'hdiutil create -srcfolder "{dmg_dir}" -volname "qtPicColor v{version}" -fs HFS+ -fsargs "-c c=64,a=16,e=16" -format UDRW -size 200m "{temp_dmg}"'
        if not run_command(cmd):
            print("hdiutil create失败")
            return False
        
        # 挂载DMG进行自定义
        mount_dir = f"/Volumes/qtPicColor v{version}"
        cmd = f'hdiutil attach "{temp_dmg}" -readwrite -mount required'
        if not run_command(cmd):
            print("hdiutil attach失败")
            return False
        
        # 等待挂载完成
        import time
        time.sleep(2)
        
        # 卸载DMG
        run_command(f'hdiutil detach "{mount_dir}"')
        
        # 转换为只读DMG
        cmd = f'hdiutil convert "{temp_dmg}" -format UDZO -imagekey zlib-level=9 -o "{dmg_path}"'
        if not run_command(cmd):
            print("hdiutil convert失败")
            return False
        
        # 清理临时文件
        if temp_dmg.exists():
            temp_dmg.unlink()
        
        print(f"✓ 备用方案DMG创建成功: {dmg_path}")
        return True
        
    except Exception as e:
        print(f"备用DMG创建失败: {e}")
        return False

def create_versioned_archives(version, dry_run=False):
    """创建带版本号的压缩包和安装包"""
    if dry_run:
        print("(干运行模式) 跳过压缩包和安装包创建")
        return True
    
    try:
        if sys.platform == 'darwin':
            # macOS: 创建DMG和便携版ZIP
            if Path("dist/qtPicColor.app").exists():
                # 创建DMG安装包
                create_dmg(version, dry_run)
                
                # 创建便携版ZIP
                archive_name = f"qtPicColor-v{version}-macOS-Portable.zip"
                run_command(f"cd dist && zip -r {archive_name} qtPicColor.app")
                print(f"macOS便携版创建成功: dist/{archive_name}")
        elif sys.platform == 'win32':
            # Windows: 创建带版本号的ZIP
            if Path("dist/qtPicColor").exists():
                archive_name = f"qtPicColor-v{version}-Windows-Portable.zip"
                import zipfile
                with zipfile.ZipFile(f"dist/{archive_name}", 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk("dist/qtPicColor"):
                        for file in files:
                            file_path = Path(root) / file
                            arcname = file_path.relative_to("dist")
                            zipf.write(file_path, arcname)
                print(f"Windows便携版创建成功: dist/{archive_name}")
        
        return True
    except Exception as e:
        print(f"创建压缩包时出错: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='qtPicColor 本地构建脚本')
    parser.add_argument('--dry-run', action='store_true', 
                       help='干运行模式，验证配置但不实际构建')
    args = parser.parse_args()
    
    if args.dry_run:
        print("=== 干运行模式 - 验证构建配置 ===")
    else:
        print("开始本地构建过程...")
    
    # 检查是否在正确的目录
    if not Path("src/qtpiccolor").exists():
        print("错误: 请在项目根目录运行此脚本")
        return 1
    
    # 获取版本号
    version = get_version()
    if not version:
        print("错误: 无法获取版本号")
        return 1
    
    print(f"项目版本: {version}")
    
    # 创建图标文件
    if not create_icon(dry_run=args.dry_run):
        if not args.dry_run:
            print("警告: 图标文件创建失败，但继续构建")
    
    # 创建Windows版本信息文件
    if not create_version_info_file(version, dry_run=args.dry_run):
        print("警告: Windows版本信息文件创建失败，但继续构建")
    
    # 创建spec文件
    if not create_spec_file(version, dry_run=args.dry_run):
        print("spec文件创建失败")
        return 1
    
    # 安装PyInstaller（如果未安装）
    print("检查PyInstaller...")
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        if args.dry_run:
            print("(干运行模式) PyInstaller未安装，但跳过安装")
        else:
            print("安装PyInstaller...")
            if not run_command(f"{sys.executable} -m pip install pyinstaller"):
                print("安装PyInstaller失败")
                return 1
    
    if args.dry_run:
        # 在macOS上检查DMG创建工具
        if sys.platform == 'darwin':
            print("检查macOS DMG创建工具...")
            create_dmg_available = run_command("which create-dmg", dry_run=True)
            hdiutil_available = run_command("which hdiutil", dry_run=True)
            
            if create_dmg_available:
                print("✓ create-dmg 工具可用")
            elif hdiutil_available:
                print("✓ hdiutil 工具可用 (备用方案)")
            else:
                print("⚠ 警告: 没有找到DMG创建工具，建议安装 create-dmg:")
                print("  brew install create-dmg")
        
        print("=== 干运行完成 - 配置验证通过 ===")
        return 0
    
    # 清理之前的构建
    if Path("dist").exists():
        print("清理之前的构建...")
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # 运行PyInstaller
    print("开始PyInstaller构建...")
    if not run_command("pyinstaller qtpiccolor.spec --clean --noconfirm"):
        print("PyInstaller构建失败")
        return 1
    
    # 检查构建结果
    if sys.platform == 'darwin':
        app_path = Path("dist/qtPicColor.app")
        if app_path.exists():
            print(f"macOS应用构建成功: {app_path}")
        else:
            print("macOS应用构建失败")
            return 1
    else:
        exe_path = Path("dist/qtPicColor")
        if exe_path.exists():
            print(f"应用构建成功: {exe_path}")
        else:
            print("应用构建失败")
            return 1
    
    # 创建带版本号的压缩包和安装包
    create_versioned_archives(version)
    
    print("本地构建完成!")
    print(f"构建结果位于: {Path('dist').absolute()}")
    print(f"版本: {version}")
    
    # 显示生成的文件
    dist_path = Path("dist")
    if dist_path.exists():
        print("\n生成的文件:")
        for file in dist_path.iterdir():
            if file.is_file() and (file.suffix in ['.dmg', '.zip'] or file.name.endswith('.exe')):
                size_mb = file.stat().st_size / 1024 / 1024
                print(f"  - {file.name} ({size_mb:.1f} MB)")
        
        if sys.platform == 'darwin' and (dist_path / "qtPicColor.app").exists():
            app_size = sum(f.stat().st_size for f in (dist_path / "qtPicColor.app").rglob('*') if f.is_file())
            print(f"  - qtPicColor.app ({app_size / 1024 / 1024:.1f} MB)")
        elif sys.platform == 'win32' and (dist_path / "qtPicColor").exists():
            folder_size = sum(f.stat().st_size for f in (dist_path / "qtPicColor").rglob('*') if f.is_file())
            print(f"  - qtPicColor/ ({folder_size / 1024 / 1024:.1f} MB)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 