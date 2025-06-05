#!/usr/bin/env python3
"""
版本提取脚本 - 从 pyproject.toml 中提取版本号
"""

import sys
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

def main():
    """主函数"""
    version = get_version()
    if version:
        print(version)
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 