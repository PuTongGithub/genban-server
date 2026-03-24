"""阿里云 DashScope 多模态模型提供者实现"""

from src.agent.entities import Message
from src.model.entities import CallResponse
from src.model.message_formatter import (
    convert_messages_for_multimodal_model,
    convert_to_call_response,
    pass_through_content,
)
from src.model.model_provider import ModelProvider
from src.provider.api import api_dashscope


class DashScopeMultiProvider(ModelProvider):
    """阿里云 DashScope 多模态模型提供者"""

    def call(
        self,
        model: str,
        messages: list[Message],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ) -> CallResponse:
        """同步调用模型"""
        # 将 Message 列表转换为多模态模型所需的字典格式
        converted_messages = convert_messages_for_multimodal_model(messages)
        response = api_dashscope.call_multimodal(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            response_format_type=response_format_type,
        )
        return convert_to_call_response(response, pass_through_content)

    def stream_call(
        self,
        model: str,
        messages: list[Message],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ):
        """流式调用模型"""
        # 将 Message 列表转换为多模态模型所需的字典格式
        converted_messages = convert_messages_for_multimodal_model(messages)
        for response in api_dashscope.stream_call_multimodal(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            response_format_type=response_format_type,
        ):
            yield convert_to_call_response(response, pass_through_content)
