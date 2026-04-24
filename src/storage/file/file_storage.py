import json
from enum import Enum, auto
from pathlib import Path
from typing import List

import magic


class FileType(Enum):
    """文件类型枚举"""

    TEXT = auto()  # 文本类型
    IMAGE = auto()  # 图片类型
    VIDEO = auto()  # 视频类型
    AUDIO = auto()  # 音频类型
    OTHER = auto()  # 其他类型


# 被视为文本文件的 MIME 类型前缀和具体类型
_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIME_TYPES = {
    "application/json",
    "application/javascript",
    "application/xml",
    "application/x-yaml",
    "application/x-shellscript",
    "application/sql",
    "application/x-httpd-php",
}

# 图片类型 MIME 前缀
_IMAGE_MIME_PREFIXES = ("image/",)

# 视频类型 MIME 前缀
_VIDEO_MIME_PREFIXES = ("video/",)

# 音频类型 MIME 前缀
_AUDIO_MIME_PREFIXES = ("audio/",)


# 文件存储底层操作类
class _FileStorage:
    # 追加写入 JSONL 文件
    def append_to_jsonl(self, file_path: Path, records: List[dict]) -> None:
        if not records:
            return

        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "a", encoding="utf-8") as f:
            for record in records:
                json_line = json.dumps(record, ensure_ascii=False)
                f.write(json_line + "\n")

    # 读取 JSONL 文件，解析错误抛异常
    def read_jsonl(self, file_path: Path) -> List[dict]:
        if not file_path.exists():
            return []

        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"JSONL parse error at {file_path}:{line_num}", e.doc, e.pos
                    )

        return records

    # 读取文本文件内容
    def read_text(self, file_path: Path) -> str:
        if not file_path.exists():
            return ""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # 读取文本文件内容为行列表
    def read_lines(self, file_path: Path) -> List[str]:
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return f.readlines()

    # 写入文本文件内容（覆盖）
    def write_text(self, file_path: Path, content: str) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 写入行列表到文本文件（覆盖）
    def write_lines(self, file_path: Path, lines: List[str]) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    # 列出目录内容
    def list_dir(self, dir_path: Path) -> List[Path]:
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        return list(dir_path.iterdir())

    # 检查路径是否存在
    def exists(self, path: Path) -> bool:
        return path.exists()

    # 检查路径是否是文件
    def is_file(self, path: Path) -> bool:
        return path.is_file()

    # 检查路径是否是目录
    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    # 写入二进制文件内容（覆盖）
    def write_bytes(self, file_path: Path, content: bytes) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)

    # 获取文件的 MIME 类型
    def get_mime_type(self, file_path: Path) -> str:
        """获取文件的 MIME 类型

        优先使用 python-magic 检测，如果不可用则兜底返回 application/octet-stream

        Args:
            file_path: 文件路径

        Returns:
            MIME 类型字符串
        """
        try:
            return magic.from_file(str(file_path), mime=True)
        except Exception:
            return "application/octet-stream"

    # 获取文件类型
    def get_file_type(self, file_path: Path) -> FileType:
        """获取文件类型（文本、图片、视频、音频、其他）

        Args:
            file_path: 文件路径

        Returns:
            FileType 枚举值
        """
        mime = self.get_mime_type(file_path)

        # 检查文本类型
        if mime.startswith(_TEXT_MIME_PREFIXES) or mime in _TEXT_MIME_TYPES:
            return FileType.TEXT

        # 检查图片类型
        if mime.startswith(_IMAGE_MIME_PREFIXES):
            return FileType.IMAGE

        # 检查视频类型
        if mime.startswith(_VIDEO_MIME_PREFIXES):
            return FileType.VIDEO

        # 检查音频类型
        if mime.startswith(_AUDIO_MIME_PREFIXES):
            return FileType.AUDIO

        # 其他类型
        return FileType.OTHER

    # 检查文件是否为文本文件
    def is_text_file(self, file_path: Path) -> bool:
        """检查文件是否为文本文件

        基于 MIME 类型判断，支持 text/* 及常见的代码文件类型

        Args:
            file_path: 文件路径

        Returns:
            是否为文本文件
        """
        return self.get_file_type(file_path) == FileType.TEXT


file_storage = _FileStorage()
