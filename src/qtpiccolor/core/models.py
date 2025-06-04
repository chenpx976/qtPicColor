"""数据模型定义"""

from dataclasses import dataclass
from typing import Tuple, List
import colorsys


@dataclass
class ColorInfo:
    """颜色信息数据模型"""
    rgb: Tuple[int, int, int]
    hex_code: str
    percentage: float
    pixel_count: int

    @property
    def hsl(self) -> Tuple[float, float, float]:
        """RGB 转 HSL"""
        r, g, b = [x / 255.0 for x in self.rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        return (h * 360, s * 100, l * 100)

    @property
    def hsv(self) -> Tuple[float, float, float]:
        """RGB 转 HSV"""
        r, g, b = [x / 255.0 for x in self.rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return (h * 360, s * 100, v * 100)

    def __str__(self) -> str:
        return f"ColorInfo(hex={self.hex_code}, percentage={self.percentage:.1f}%)"


@dataclass
class ImageInfo:
    """图像信息数据模型"""
    file_path: str
    width: int
    height: int
    format: str
    size_bytes: int
    colors: List[ColorInfo]
    analysis_time: float

    def __str__(self) -> str:
        return f"ImageInfo({self.file_path}, {len(self.colors)} colors)" 