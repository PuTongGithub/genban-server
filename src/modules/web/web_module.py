"""Web工具模块"""

from src.modules.base_module import BaseModule
from src.modules.web.fetch.web_fetch_tool import WebFetchTool
from src.modules.web.search.web_search_tool import WebSearchTool
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook


class WebModule(BaseModule):
    """Web工具模块"""

    id = "web"
    name = "Web工具模块"
    description = "提供了一定的互联网内容访问能力"

    def __init__(self) -> None:
        """初始化Web工具模块，创建工具实例"""
        self._tools: list[BaseTool] = [
            WebFetchTool(),
            WebSearchTool(),
        ]
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
