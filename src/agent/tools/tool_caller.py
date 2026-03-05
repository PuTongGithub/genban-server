"""工具调用器"""

import json

from src.agent.tools.base_tool import BaseTool
from src.agent.tools.tool_registry import ToolRegistry
from src.agent.entities import ToolCall, ToolResult
from src.agent.tools.tool_parser import ToolParser


class ToolCaller:
    """工具调用器"""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        self.parser = ToolParser()

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self.registry.register(tool)

    def register_many(self, tools: list[BaseTool]) -> None:
        """批量注册工具"""
        self.registry.register_many(tools)

    def execute(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        """执行工具调用"""
        results: list[ToolResult] = []
        for call in tool_calls:
            tool = self.registry.get(call.name)
            try:
                result = tool.execute(**call.arguments)
                if not isinstance(result, str):
                    result = json.dumps(result, ensure_ascii=False)
            except Exception as e:
                result = json.dumps({"error": str(e)}, ensure_ascii=False)

            results.append(ToolResult(tool_call_id=call.id, content=result))
        return results

    def execute_from_model_response(
        self, tool_calls_data: list[dict]
    ) -> list[ToolResult]:
        """从模型响应中解析并执行工具调用"""
        tool_calls = self.parser.parse_tool_calls(tool_calls_data)
        return self.execute(tool_calls)

    def get_tools_schemas(self) -> list[dict]:
        """获取所有工具的 Schema"""
        return self.registry.get_all_schemas()
