"""历史记录管理器"""

import os
import uuid
import json
import shutil
from typing import List, Optional, Dict
from pathlib import Path
from datetime import datetime
from PIL import Image

from .models import HistoryRecord, ImageInfo


class HistoryManager:
    """历史记录管理器"""

    def __init__(self, history_dir: str = None):
        """
        初始化历史记录管理器

        Args:
            history_dir: 历史记录存储目录
        """
        if history_dir is None:
            # 默认使用用户主目录下的应用数据目录
            home_dir = Path.home()
            history_dir = home_dir / ".qtpiccolor" / "history"

        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # 缩略图目录
        self.thumbnails_dir = self.history_dir / "thumbnails"
        self.thumbnails_dir.mkdir(exist_ok=True)

        # 历史记录索引文件
        self.index_file = self.history_dir / "index.json"

        self._records: List[HistoryRecord] = []
        self._load_index()

    def add_record(self, image_info: ImageInfo) -> HistoryRecord:
        """
        添加历史记录

        Args:
            image_info: 图片分析信息

        Returns:
            创建的历史记录
        """
        # 生成唯一ID
        record_id = str(uuid.uuid4())

        # 生成缩略图
        thumbnail_path = self._create_thumbnail(image_info.file_path, record_id)

        # 创建历史记录
        record = HistoryRecord(
            id=record_id, image_info=image_info, thumbnail_path=thumbnail_path
        )

        # 添加到列表开头（最新的在前面）
        self._records.insert(0, record)

        # 限制历史记录数量（最多保存100条）
        if len(self._records) > 100:
            removed_record = self._records.pop()
            self._remove_thumbnail(removed_record.id)

        # 保存索引
        self._save_index()

        return record

    def get_records(self, limit: int = None) -> List[HistoryRecord]:
        """
        获取历史记录列表

        Args:
            limit: 限制返回的记录数量

        Returns:
            历史记录列表
        """
        if limit is None:
            return self._records.copy()
        return self._records[:limit]

    def get_record_by_id(self, record_id: str) -> Optional[HistoryRecord]:
        """
        根据ID获取历史记录

        Args:
            record_id: 记录ID

        Returns:
            历史记录，如果不存在则返回None
        """
        for record in self._records:
            if record.id == record_id:
                return record
        return None

    def remove_record(self, record_id: str) -> bool:
        """
        删除历史记录

        Args:
            record_id: 记录ID

        Returns:
            是否删除成功
        """
        for i, record in enumerate(self._records):
            if record.id == record_id:
                # 删除缩略图
                self._remove_thumbnail(record_id)

                # 从列表中删除
                self._records.pop(i)

                # 保存索引
                self._save_index()

                return True
        return False

    def clear_all(self):
        """清空所有历史记录"""
        # 删除所有缩略图
        for record in self._records:
            self._remove_thumbnail(record.id)

        # 清空列表
        self._records.clear()

        # 保存索引
        self._save_index()

    def _create_thumbnail(self, image_path: str, record_id: str) -> str:
        """
        创建缩略图

        Args:
            image_path: 原图路径
            record_id: 记录ID

        Returns:
            缩略图路径
        """
        try:
            # 打开原图
            with Image.open(image_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # 创建缩略图（200x200）
                img.thumbnail((200, 200), Image.Resampling.LANCZOS)

                # 保存缩略图
                thumbnail_path = self.thumbnails_dir / f"{record_id}.jpg"
                img.save(thumbnail_path, "JPEG", quality=85)

                return str(thumbnail_path)
        except Exception as e:
            print(f"创建缩略图失败: {e}")
            return None

    def _remove_thumbnail(self, record_id: str):
        """删除缩略图"""
        thumbnail_path = self.thumbnails_dir / f"{record_id}.jpg"
        if thumbnail_path.exists():
            try:
                thumbnail_path.unlink()
            except Exception as e:
                print(f"删除缩略图失败: {e}")

    def _load_index(self):
        """加载历史记录索引"""
        if not self.index_file.exists():
            return

        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 重建历史记录列表
            self._records.clear()
            for record_data in data.get("records", []):
                try:
                    record = self._dict_to_record(record_data)
                    self._records.append(record)
                except Exception as e:
                    print(f"加载历史记录失败: {e}")

        except Exception as e:
            print(f"加载历史记录索引失败: {e}")

    def _save_index(self):
        """保存历史记录索引"""
        try:
            data = {
                "version": "1.0",
                "records": [self._record_to_dict(record) for record in self._records],
            }

            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存历史记录索引失败: {e}")

    def _record_to_dict(self, record: HistoryRecord) -> Dict:
        """将历史记录转换为字典"""
        return {
            "id": record.id,
            "thumbnail_path": record.thumbnail_path,
            "created_at": record.created_at.isoformat(),
            "image_info": {
                "file_path": record.image_info.file_path,
                "width": record.image_info.width,
                "height": record.image_info.height,
                "size_bytes": record.image_info.size_bytes,
                "analysis_time": record.image_info.analysis_time,
                "timestamp": record.image_info.timestamp,
                "format": getattr(record.image_info, "format", "Unknown"),
                "colors": [
                    {
                        "rgb": color.rgb,
                        "hex_code": color.hex_code,
                        "percentage": color.percentage,
                        "position": color.position,
                    }
                    for color in record.image_info.colors
                ],
            },
        }

    def _dict_to_record(self, data: Dict) -> HistoryRecord:
        """将字典转换为历史记录"""
        from .models import ColorInfo

        # 重建颜色信息
        colors = []
        for color_data in data["image_info"]["colors"]:
            color = ColorInfo(
                rgb=tuple(color_data["rgb"]),
                hex_code=color_data["hex_code"],
                percentage=color_data["percentage"],
                position=color_data.get("position"),
            )
            colors.append(color)

        # 重建图片信息
        image_info = ImageInfo(
            file_path=data["image_info"]["file_path"],
            width=data["image_info"]["width"],
            height=data["image_info"]["height"],
            size_bytes=data["image_info"]["size_bytes"],
            colors=colors,
            analysis_time=data["image_info"]["analysis_time"],
            format=data["image_info"].get("format", "Unknown"),
            timestamp=data["image_info"]["timestamp"],
        )

        # 重建历史记录
        record = HistoryRecord(
            id=data["id"],
            image_info=image_info,
            thumbnail_path=data.get("thumbnail_path"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

        return record
