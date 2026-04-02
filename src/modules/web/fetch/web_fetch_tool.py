"""网页获取工具"""

from typing import Any

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.modules.web.fetch.web_fetch_util import fetch_webpage

logger = get_logger(__name__)


class WebFetchTool(BaseTool):
    """网页获取工具"""

    name = "web_fetch"
    description = "获取指定网页的内容，返回Markdown格式的文本"
    parameters = [
        ToolParameter(
            name="url",
            type="string",
            description="要获取的网页URL，例如：https://www.baidu.com",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行网页获取操作

        Args:
            context: Agent 执行上下文
            url: 要获取的网页URL

        Returns:
            网页内容的Markdown格式文本，失败时返回错误信息
        """
        url = kwargs.get("url", "")

        if not url.strip():
            return chat_factory.create_system_remainder_str("错误：URL不能为空")

        try:
            content = fetch_webpage(url)
            if content:
                return content
            else:
                logger.warning(f"网页内容获取失败，user_id: {context.user_id}, url: {url}")
                return chat_factory.create_system_remainder_str(
                    f"错误：无法获取网页内容，请检查URL是否正确: {url}"
                )
        except Exception as e:
            logger.exception(f"网页获取过程发生异常，user_id: {context.user_id}, url: {url}")
            return chat_factory.create_system_remainder_str(f"错误：获取网页时发生异常: {e}")
