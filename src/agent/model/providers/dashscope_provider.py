"""阿里云 DashScope 模型提供者实现"""

import dashscope  # type: ignore
from src.config.config import env_config
from src.agent.model.model_provider import ModelProvider
from src.agent.entities import CallResponse, Message


class DashScopeProvider(ModelProvider):
    """阿里云 DashScope 模型提供者"""

    def call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = False,
    ) -> CallResponse:
        """同步调用模型"""
        kwargs = {
            "api_key": env_config.get("DASHSCOPE_API_KEY"),
            "model": model,
            "messages": messages,
            "tools": tools,
            "enable_thinking": enable_thinking,
            "result_format": "message",
            "stream": False,
            "parallel_tool_calls": True,
        }
        response = dashscope.Generation.call(**kwargs)
        return self._convert_to_call_response(response)

    def stream_call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = False,
    ):
        """流式调用模型"""
        kwargs = {
            "api_key": env_config.get("DASHSCOPE_API_KEY"),
            "model": model,
            "messages": messages,
            "tools": tools,
            "enable_thinking": enable_thinking,
            "result_format": "message",
            "stream": True,
            "parallel_tool_calls": True,
        }
        responses = dashscope.Generation.call(**kwargs)
        for response in responses:
            yield self._convert_to_call_response(response)

    def _convert_to_call_response(self, response) -> CallResponse:
        """将 DashScope 响应转换为 CallResponse

        Args:
            response: DashScope 响应对象

        Returns:
            CallResponse 实例
        """
        output = response.output
        usage = response.usage

        message_data = output.choices[0].message
        message = Message(
            role=message_data.role,
            content=message_data.content,
            reasoning_content=getattr(message_data, "reasoning_content", ""),
            tool_calls=getattr(message_data, "tool_calls", None),
            tool_call_id=getattr(message_data, "tool_call_id", None),
        )

        return CallResponse(
            request_id=response.request_id,
            status_code=response.status_code,
            total_tokens=usage.total_tokens,
            finish_reason=output.choices[0].finish_reason,
            message=message,
        )
