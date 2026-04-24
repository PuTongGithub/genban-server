"""文件分享链接生成器"""

from src.config.config import app_config


class FileShareLinkGenerator:
    """生成文件分享链接的工具类"""

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
