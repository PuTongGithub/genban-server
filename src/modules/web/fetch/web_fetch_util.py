"""网页获取工具模块 - 使用Scrapling+markdownify实现"""

from markdownify import markdownify as md
from scrapling import StealthyFetcher

from src.agent.chat_factory import chat_factory
from src.common.logger import get_logger

logger = get_logger(__name__)


def fetch_webpage(url: str) -> str:
    """获取网页内容并转换为Markdown格式

    Args:
        url: 目标网页URL

    Returns:
        网页内容的Markdown格式文本，失败时抛出异常
    """
    try:
        fetcher = StealthyFetcher(auto=True)
        page = fetcher.fetch(url)
        if not page:
            return chat_factory.create_system_remainder_str(
                "无法获取网页内容，可能是链接无效或反爬太严"
            )

        markdown_content = md(page.html_content, heading_style="ATX")
        return markdown_content
    except Exception:
        logger.exception(f"获取网页内容失败，url: {url}")
        return chat_factory.create_system_remainder_str("获取网页内容异常")
