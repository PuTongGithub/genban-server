"""阿里云 DashScope 模型提供者实现"""

from src.agent.entities import Message
from src.model.entities import CallResponse
from src.model.message_formatter import (
    convert_messages_for_text_model,
    convert_to_call_response,
    format_text_content,
)
from src.model.model_provider import ModelProvider
from src.provider.api import api_dashscope


class DashScopeProvider(ModelProvider):
    """阿里云 DashScope 模型提供者"""

    def call(
        self,
        model: str,
        messages: list[Message],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ) -> CallResponse:
        """同步调用模型"""
        # 将 Message 列表转换为纯文本模型所需的字典格式
        converted_messages = convert_messages_for_text_model(messages)
        response = api_dashscope.call(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            response_format_type=response_format_type,
        )
        return convert_to_call_response(response, content_formatter=format_text_content)

    def stream_call(
        self,
        model: str,
        messages: list[Message],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ):
        """流式调用模型"""
        # 将 Message 列表转换为纯文本模型所需的字典格式
        converted_messages = convert_messages_for_text_model(messages)
        for response in api_dashscope.stream_call(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            response_format_type=response_format_type,
        ):
            yield convert_to_call_response(
                response, content_formatter=format_text_content
            )
