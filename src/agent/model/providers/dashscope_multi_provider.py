"""阿里云 DashScope 多模态模型提供者实现"""

import dashscope  # type: ignore
from src.config.config import env_config
from src.agent.model.model_provider import ModelProvider
from src.agent.entities import CallResponse, Message
from src.agent.exceptions import ModelResponseException


class DashScopeMultiProvider(ModelProvider):
    """阿里云 DashScope 多模态模型提供者"""

    def call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = True,
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
        response = dashscope.MultiModalConversation.call(**kwargs)
        return self._convert_to_call_response(response)

    def stream_call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = True,
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
            "incremental_output": False,
        }
        responses = dashscope.MultiModalConversation.call(**kwargs)
        for response in responses:
            yield self._convert_to_call_response(response)

    def _convert_to_call_response(self, response) -> CallResponse:
        """将 DashScope 响应转换为 CallResponse

        Args:
            response: DashScope 响应对象

        Returns:
            CallResponse 实例

        Raises:
            ModelResponseException: 当响应格式异常时抛出
        """
        output = response.output
        usage = response.usage

        if output is None or not hasattr(output, "choices") or output.choices is None:
            raise ModelResponseException(f"DashScope 响应异常：{response}", response)

        message_data = output.choices[0].message
        message = Message(
            role=message_data.role,
            content=message_data.content,
            reasoning_content=message_data["reasoning_content"]
            if "reasoning_content" in message_data
            else "",
            tool_calls=message_data["tool_calls"]
            if "tool_calls" in message_data
            else None,
            tool_call_id=message_data["tool_call_id"]
            if "tool_call_id" in message_data
            else None,
        )

        return CallResponse(
            request_id=response.request_id,
            status_code=response.status_code,
            total_tokens=usage.total_tokens,
            finish_reason=output.choices[0].finish_reason,
            message=message,
        )
