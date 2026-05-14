"""工具调用器"""

import json

from src.agent.entities import AgentContext
from src.agent.entities import ToolCall as ModelToolCall
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolCall, ToolResult, ToolExecute
from src.agent.tools.tool_registry import ToolRegistry
from src.common.logger import get_logger
from src.config.config import app_config

logger = get_logger(__name__)


class ToolCaller:
    """工具调用器"""

    def __init__(self, registry: ToolRegistry | None = None) -> None:
        self.registry = registry or ToolRegistry()
        # 获取工具返回的最大字符串长度
        max_token = app_config.get("conversation_memory", {}).get("max_token", 20000)
        self._max_tool_result_length = max(10000, max_token // 3 * 2)

    def register(self, tool: BaseTool) -> None:
        """注册工具"""
        self.registry.register(tool)

    def register_many(self, tools: list[BaseTool]) -> None:
        """批量注册工具"""
        self.registry.register_many(tools)

    def execute(self, tool_calls: list[ToolCall], context: AgentContext) -> list[ToolResult]:
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
                if isinstance(result, str):
                    result = self._handel_tool_result_content(result)
                    results.append(ToolResult(tool_call_id=call.id, result=ToolExecute(result_content=result)))
                elif isinstance(result, ToolExecute):
                    result.result_content = self._handel_tool_result_content(result.result_content)
                    results.append(ToolResult(tool_call_id=call.id, result=result))
            except Exception as e:
                logger.exception("执行工具调用失败")
                result = self._handel_tool_result_content(str(e))
                results.append(ToolResult(tool_call_id=call.id, result=ToolExecute(result_content=result, error=True)))
        return results

    def execute_from_model_response(
        self, tool_calls_data: list[ModelToolCall], context: AgentContext
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
            return [ToolResult(tool_call_id="", result=ToolExecute(result_content="工具调用参数解析失败", error=True))]
        else:
            return self.execute(tool_calls, context)

    def get_tools_schemas(self) -> list[dict] | None:
        """获取所有工具的 Schema"""
        schemas = self.registry.get_all_schemas()
        return len(schemas) > 0 and schemas or None

    def _parse_tool_calls(self, tool_calls_data: list[ModelToolCall]) -> list[ToolCall]:
        """解析工具调用数据"""
        tool_calls: list[ToolCall] = []
        for call_data in tool_calls_data:
            try:
                arguments: dict = {}
                arguments_str = call_data.function.arguments or "{}"
                if isinstance(arguments_str, str):
                    arguments = json.loads(arguments_str)
                else:
                    arguments = arguments_str

                tool_calls.append(
                    ToolCall(id=call_data.id, name=call_data.function.name, arguments=arguments)
                )
            except Exception:
                logger.exception("解析工具调用数据失败")
        return tool_calls

    def _handel_tool_result_content(self, tool_content: str) -> str:
        """处理工具返回结果内容"""
        if len(tool_content) > self._max_tool_result_length:
            tool_content = tool_content[:self._max_tool_result_length] + "\n\n[系统提醒：数据过长，已被截断]"
        return tool_content