"""数据模型定义"""

from dataclasses import dataclass
from typing import Tuple, List, Optional
import colorsys
import time
from datetime import datetime


@dataclass
class ColorInfo:
    """颜色信息数据模型"""

    rgb: Tuple[int, int, int]
    hex_code: str
    percentage: float
    position: Optional[Tuple[int, int]] = None

    @property
    def hsl(self) -> Tuple[float, float, float]:
        """RGB 转 HSL"""
        r, g, b = [x / 255.0 for x in self.rgb]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Lightness
        l = (max_val + min_val) / 2

        if diff == 0:
            h = s = 0
        else:
            # Saturation
            s = (
                diff / (2 - max_val - min_val)
                if l > 0.5
                else diff / (max_val + min_val)
            )

            # Hue
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6

        return (h * 360, s * 100, l * 100)

    @property
    def hsv(self) -> Tuple[float, float, float]:
        """RGB 转 HSV"""
        r, g, b = [x / 255.0 for x in self.rgb]
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val

        # Value
        v = max_val

        # Saturation
        s = 0 if max_val == 0 else diff / max_val

        # Hue
        if diff == 0:
            h = 0
        elif max_val == r:
            h = (g - b) / diff + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / diff + 2
        else:
            h = (r - g) / diff + 4
        h /= 6

        return (h * 360, s * 100, v * 100)

    def __str__(self) -> str:
        return f"ColorInfo(hex={self.hex_code}, percentage={self.percentage:.1f}%)"


@dataclass
class ImageInfo:
    """图像信息数据模型"""

    file_path: str
    width: int
    height: int
    size_bytes: int
    colors: List[ColorInfo]
    analysis_time: float
    format: str = "Unknown"  # 图像格式，设为可选参数
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def __str__(self) -> str:
        return f"ImageInfo({self.file_path}, {len(self.colors)} colors)"


@dataclass
class HistoryRecord:
    """历史记录"""

    id: str
    image_info: ImageInfo
    thumbnail_path: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def display_name(self) -> str:
        """显示名称"""
        import os

        base_name = os.path.basename(self.image_info.file_path)
        time_str = self.created_at.strftime("%H:%M:%S")
        return f"{base_name} ({time_str})"

    @property
    def file_size_mb(self) -> float:
        """文件大小（MB）"""
        return self.image_info.size_bytes / (1024 * 1024)

    @property
    def color_count(self) -> int:
        """颜色数量"""
        return len(self.image_info.colors)
