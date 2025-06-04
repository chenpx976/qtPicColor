#!/usr/bin/env python3
"""
本地构建脚本 - 用于测试PyInstaller打包
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """运行命令并检查结果"""
    print(f"运行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"命令执行失败: {result.stderr}")
        return False
    print(f"命令输出: {result.stdout}")
    return True

def create_icon():
    """创建默认图标文件"""
    try:
        from PIL import Image, ImageDraw
        
        # 确保资源目录存在
        resources_dir = Path("src/qtpiccolor/resources")
        resources_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建一个简单的图标
        img = Image.new('RGBA', (256, 256), (70, 130, 180, 255))
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 50, 206, 206], fill=(255, 255, 255, 255))
        draw.text((100, 120), 'QPC', fill=(70, 130, 180, 255))
        
        # 保存为不同格式
        if sys.platform == 'win32':
            img.save('src/qtpiccolor/resources/icon.ico', format='ICO', 
                    sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        else:
            img.save('src/qtpiccolor/resources/icon.png')
            # 在macOS上，可以使用iconutil创建.icns文件
            if sys.platform == 'darwin':
                # 创建iconset目录
                iconset_dir = Path("src/qtpiccolor/resources/icon.iconset")
                iconset_dir.mkdir(exist_ok=True)
                
                # 创建不同尺寸的图标
                sizes = [16, 32, 64, 128, 256, 512]
                for size in sizes:
                    resized = img.resize((size, size), Image.Resampling.LANCZOS)
                    resized.save(iconset_dir / f"icon_{size}x{size}.png")
                    if size <= 256:
                        resized.save(iconset_dir / f"icon_{size}x{size}@2x.png")
                
                # 使用iconutil创建.icns文件
                run_command(f"iconutil -c icns {iconset_dir}")
                
        print("图标文件创建成功")
        return True
    except ImportError:
        print("警告: PIL未安装，无法创建图标文件")
        return False
    except Exception as e:
        print(f"创建图标文件时出错: {e}")
        return False

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None

# 获取源码路径
src_path = Path('src')

a = Analysis(
    ['src/qtpiccolor/__main__.py'],
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        ('src/qtpiccolor/resources', 'qtpiccolor/resources'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'PIL',
        'numpy',
        'sklearn',
        'skimage',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Image',
                    'CFBundleTypeRole': 'Viewer',
                    'LSItemContentTypes': ['public.image'],
                }
            ]
        },
    )
'''
    
    with open('qtpiccolor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("PyInstaller spec文件创建成功")

def main():
    """主函数"""
    print("开始本地构建过程...")
    
    # 检查是否在正确的目录
    if not Path("src/qtpiccolor").exists():
        print("错误: 请在项目根目录运行此脚本")
        return 1
    
    # 创建图标文件
    create_icon()
    
    # 创建spec文件
    create_spec_file()
    
    # 安装PyInstaller（如果未安装）
    print("检查PyInstaller...")
    try:
        import PyInstaller
        print("PyInstaller已安装")
    except ImportError:
        print("安装PyInstaller...")
        if not run_command(f"{sys.executable} -m pip install pyinstaller"):
            print("安装PyInstaller失败")
            return 1
    
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
    
    print("本地构建完成!")
    print(f"构建结果位于: {Path('dist').absolute()}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 