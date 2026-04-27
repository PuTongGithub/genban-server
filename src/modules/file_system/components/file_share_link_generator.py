"""文件分享链接生成器与 Base64 编码工具"""

import base64
import re
from pathlib import Path

from src.common.utils.file_type_util import FileTypeUtil
from src.config.config import app_config


class FileShareLinkGenerator:
    """生成文件分享链接的工具类"""

    _SHARE_LINK_PATTERN = re.compile(r"/api/file_system/share/([^/]+)/(.+)")

    @staticmethod
    def generate_link(user_id: str, path: str) -> str:
        """生成文件分享链接

        Args:
            user_id: 用户ID
            path: 文件相对路径

        Returns:
            完整的分享链接URL
        """
        base_url = app_config.get("server", {}).get("base_url", "")
        # 确保 path 不以 / 开头，避免 URL 中出现双斜杠
        path = path.lstrip("/")
        return f"{base_url}/api/file_system/share/{user_id}/{path}"

    @classmethod
    def is_share_link(cls, url: str) -> bool:
        """检测 URL 是否为文件分享链接格式

        Args:
            url: 图片或文件 URL

        Returns:
            是否为分享链接
        """
        if not url:
            return False
        base_url = app_config.get("server", {}).get("base_url", "")
        share_prefix = f"{base_url}/api/file_system/share/"
        return url.startswith(share_prefix)

    @classmethod
    def extract_path_from_share_link(cls, url: str) -> tuple[str, str] | None:
        """从分享链接中提取 user_id 和 path

        Args:
            url: 分享链接 URL

        Returns:
            (user_id, path) 元组，如果不是分享链接则返回 None
        """
        if not cls.is_share_link(url):
            return None

        match = cls._SHARE_LINK_PATTERN.search(url)
        if match:
            user_id = match.group(1)
            path = match.group(2)
            return user_id, path
        return None

    @classmethod
    def encode_file_to_base64(cls, file_path: Path) -> str:
        """将文件编码为 Base64 字符串

        Args:
            file_path: 文件路径

        Returns:
            Base64 编码的字符串，格式为 data:image/png;base64,xxx

        Raises:
            FileNotFoundError: 文件不存在
        """
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取文件内容
        with open(file_path, "rb") as f:
            file_data = f.read()

        # 编码为 base64
        base64_data = base64.b64encode(file_data).decode("utf-8")

        # 使用工具类获取 MIME 类型
        mime_type = FileTypeUtil.get_mime_type(file_path)

        return f"data:{mime_type};base64,{base64_data}"
