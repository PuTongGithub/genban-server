"""工具注册中心"""

from typing import Any

from src.agent.exceptions import ToolNotExistException
from src.agent.tools.base_tool import BaseTool


class ToolRegistry:
    """工具注册中心"""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def register_many(self, tools: list[BaseTool]) -> None:
        """批量注册工具"""
        for tool in tools:
            self.register(tool)

    def get(self, name: str) -> BaseTool:
        """获取工具"""
        if name not in self._tools:
            raise ToolNotExistException(name)
        return self._tools[name]

    def get_all_schemas(self) -> list[dict[str, Any]]:
        """获取所有工具的 Schema"""
        return [tool.get_schema() for tool in self._tools.values()]
