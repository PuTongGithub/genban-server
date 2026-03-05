"""工具调用数据解析"""

import json
from typing import Any

from src.agent.entities import ToolCall


class ToolParser:
    """工具调用数据解析器"""

    @staticmethod
    def parse_tool_calls(tool_calls_data: list[dict[str, Any]]) -> list[ToolCall]:
        """解析工具调用数据"""
        tool_calls: list[ToolCall] = []
        for call_data in tool_calls_data:
            arguments: dict[str, Any] = {}
            if "function" in call_data:
                func_data = call_data["function"]
                arguments_str = func_data.get("arguments", "{}")
                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str)
                else:
                    arguments = arguments_str
                name = func_data.get("name", "")
            else:
                name = call_data.get("name", "")
                arguments = call_data.get("arguments", {})

            tool_calls.append(
                ToolCall(id=call_data.get("id", ""), name=name, arguments=arguments)
            )
        return tool_calls
