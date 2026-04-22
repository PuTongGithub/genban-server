"""阿里云 DashScope 模型提供者实现"""

from src.agent.entities import Message
from src.model.entities import CallResponse, ModelCallOptions
from src.model.formatter.message_formatter import (
    convert_dashscope_to_call_response,
    convert_messages_for_text_model,
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
        base_url: str | None = None,
        api_key: str | None = None,
        options: ModelCallOptions | None = None,
    ) -> CallResponse:
        """同步调用模型"""
        converted_messages = convert_messages_for_text_model(messages)
        response = api_dashscope.call(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            options=options,
        )
        return convert_dashscope_to_call_response(response)

    def stream_call(
        self,
        model: str,
        messages: list[Message],
        tools: list | None = None,
        enable_thinking: bool = True,
        base_url: str | None = None,
        api_key: str | None = None,
        options: ModelCallOptions | None = None,
    ):
        """流式调用模型"""
        converted_messages = convert_messages_for_text_model(messages)
        for response in api_dashscope.stream_call(
            model=model,
            messages=converted_messages,
            tools=tools,
            enable_thinking=enable_thinking,
            options=options,
        ):
            yield convert_dashscope_to_call_response(response)
