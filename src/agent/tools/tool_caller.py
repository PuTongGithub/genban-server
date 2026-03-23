"""工具调用器"""

import json

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolCall, ToolResult
from src.agent.tools.tool_registry import ToolRegistry
from src.common.logger import get_logger

logger = get_logger(__name__)


class ToolCaller:
    """工具调用器"""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self.registry.register(tool)

    def register_many(self, tools: list[BaseTool]) -> None:
        """批量注册工具"""
        self.registry.register_many(tools)

    def execute(
        self, tool_calls: list[ToolCall], context: AgentContext
    ) -> list[ToolResult]:
        """执行工具调用

        Args:
            tool_calls: 工具调用列表
            context: Agent 执行上下文

        Returns:
            工具执行结果列表
        """
        results: list[ToolResult] = []
        for call in tool_calls:
            try:
                tool = self.registry.get(call.name)
                result = tool.execute(context=context, **call.arguments)
                if not isinstance(result, str):
                    result = json.dumps(result, ensure_ascii=False)
            except Exception as e:
                logger.exception("执行工具调用失败")
                result = chat_factory.create_system_remainder_str(f"Error: {str(e)}")

            results.append(ToolResult(tool_call_id=call.id, content=result))
        return results

    def execute_from_model_response(
        self, tool_calls_data: list[dict], context: AgentContext
    ) -> list[ToolResult]:
        """从模型响应中解析并执行工具调用

        Args:
            tool_calls_data: 模型返回的工具调用数据
            context: Agent 执行上下文

        Returns:
            工具执行结果列表
        """
        tool_calls = self._parse_tool_calls(tool_calls_data)
        if not tool_calls:
            return [ToolResult(tool_call_id="", content="工具调用参数解析失败")]
        else:
            return self.execute(tool_calls, context)

    def get_tools_schemas(self) -> list[dict] | None:
        """获取所有工具的 Schema"""
        schemas = self.registry.get_all_schemas()
        return len(schemas) > 0 and schemas or None

    def _parse_tool_calls(self, tool_calls_data: list[dict]) -> list[ToolCall]:
        """解析工具调用数据"""
        tool_calls: list[ToolCall] = []
        for call_data in tool_calls_data:
            try:
                arguments: dict = {}
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
            except Exception:
                logger.exception("解析工具调用数据失败")
        return tool_calls
