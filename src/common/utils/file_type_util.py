"""文件类型工具模块"""

from enum import Enum, auto
from pathlib import Path

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

# 常见文件扩展名集合
_FILE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".svg",
    ".mp4",
    ".webm",
    ".mov",
    ".avi",
    ".mp3",
    ".wav",
    ".ogg",
    ".pdf",
    ".zip",
    ".rar",
    ".7z",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".txt",
    ".json",
    ".xml",
    ".csv",
}


class FileTypeUtil:
    """文件类型工具类"""

    @staticmethod
    def get_mime_type(file_path: Path) -> str:
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

    @staticmethod
    def get_file_type(file_path: Path) -> FileType:
        """获取文件类型（文本、图片、视频、音频、其他）

        Args:
            file_path: 文件路径

        Returns:
            FileType 枚举值
        """
        mime = FileTypeUtil.get_mime_type(file_path)

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

    @staticmethod
    def is_text_file(file_path: Path) -> bool:
        """检查文件是否为文本文件

        基于 MIME 类型判断，支持 text/* 及常见的代码文件类型

        Args:
            file_path: 文件路径

        Returns:
            是否为文本文件
        """
        return FileTypeUtil.get_file_type(file_path) == FileType.TEXT

    @staticmethod
    def is_image_file(file_path: Path) -> bool:
        """检查文件是否为图片文件

        Args:
            file_path: 文件路径

        Returns:
            是否为图片文件
        """
        return FileTypeUtil.get_file_type(file_path) == FileType.IMAGE

    @staticmethod
    def is_video_file(file_path: Path) -> bool:
        """检查文件是否为视频文件

        Args:
            file_path: 文件路径

        Returns:
            是否为视频文件
        """
        return FileTypeUtil.get_file_type(file_path) == FileType.VIDEO

    @staticmethod
    def is_audio_file(file_path: Path) -> bool:
        """检查文件是否为音频文件

        Args:
            file_path: 文件路径

        Returns:
            是否为音频文件
        """
        return FileTypeUtil.get_file_type(file_path) == FileType.AUDIO

    @staticmethod
    def is_file_by_extension(path: str) -> bool:
        """根据扩展名判断是否为文件

        用于 URL 路径判断，不依赖文件实际存在

        Args:
            path: 文件路径或 URL 路径

        Returns:
            是否为文件（基于扩展名）
        """
        suffix = Path(path).suffix.lower()
        return suffix in _FILE_EXTENSIONS
