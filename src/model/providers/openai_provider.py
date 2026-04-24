"""OpenAI 兼容模型提供者实现"""

from src.agent.entities import Message
from src.common.logger import get_logger
from src.model.entities import CallResponse, ModelCallOptions
from src.model.formatter.message_formatter import (
    convert_messages_for_openai,
    convert_openai_to_call_response,
)
from src.model.model_provider import ModelProvider
from src.provider.api import api_openai

logger = get_logger(__name__)


class OpenAIProvider(ModelProvider):
    """OpenAI 兼容模型提供者"""

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
        if base_url is None:
            raise ValueError("base_url 参数不能为空")
        if api_key is None:
            raise ValueError("api_key 参数不能为空")

        converted_messages = convert_messages_for_openai(messages)
        response = api_openai.call(
            model=model,
            messages=converted_messages,
            api_key=api_key,
            base_url=base_url,
            tools=tools,
            enable_thinking=enable_thinking,
            options=options,
        )
        return convert_openai_to_call_response(response)

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
        if base_url is None:
            raise ValueError("base_url 参数不能为空")
        if api_key is None:
            raise ValueError("api_key 参数不能为空")

        converted_messages = convert_messages_for_openai(messages)
        for chunk in api_openai.stream_call(
            model=model,
            messages=converted_messages,
            api_key=api_key,
            base_url=base_url,
            tools=tools,
            enable_thinking=enable_thinking,
            options=options,
        ):
            logger.debug(chunk)
            yield convert_openai_to_call_response(chunk)
