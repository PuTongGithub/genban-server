"""模型调用器"""

from src.agent.entities import Chat, Message
from src.agent.exceptions import (
    ModelCallException,
    ModelCallLengthLimitedException,
    ModelProviderNotFoundException,
)
from src.common.logger import get_logger
from src.config.config import app_config
from src.model.entities import CallResponse
from src.model.model_provider import ModelProvider
from src.model.providers.dashscope_multi_provider import DashScopeMultiProvider
from src.model.providers.dashscope_provider import DashScopeProvider

logger = get_logger(__name__)


class ModelCaller:
    """模型调用器，统一封装不同 Provider 的调用"""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        """注册默认的模型提供者"""
        self._providers["dashscope"] = DashScopeProvider()
        self._providers["dashscope_multi"] = DashScopeMultiProvider()

    def _get_provider(self, api_name: str) -> ModelProvider:
        """获取模型提供者"""
        if api_name not in self._providers:
            raise ModelProviderNotFoundException(f"provider:{api_name}")
        return self._providers[api_name]

    def _convert_chats_to_messages(self, chats: list[Chat]) -> list[Message]:
        """将 Chat 列表转换为 Message 列表"""
        messages: list[Message] = []
        for chat in chats:
            messages.append(chat.message)
        return messages

    def _validate_response(self, response: CallResponse) -> None:
        """验证模型响应是否有效"""
        if response.status_code != 200:
            raise ModelCallException(str(response))
        if response.finish_reason == "length":
            raise ModelCallLengthLimitedException()

    def call(
        self,
        model_key: str,
        chats: list[Chat],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ) -> CallResponse:
        """调用模型"""
        logger.info(f"模型调用请求，model_key: {model_key}，chats: {str(chats)}")
        messages = self._convert_chats_to_messages(chats)
        model_config = app_config.get_model_config(model_key)
        provider = self._get_provider(model_config["api"])

        try:
            response = provider.call(
                model=model_config["id"],
                messages=messages,
                tools=tools,
                enable_thinking=enable_thinking,
                response_format_type=response_format_type,
            )
            self._validate_response(response)
            logger.info(f"模型调用成功，model_key: {model_key}，response: {str(response)}")
            return response
        except Exception:
            logger.exception(f"模型调用失败，model_key: {model_key}")
            raise

    def stream_call(
        self,
        model_key: str,
        chats: list[Chat],
        tools: list | None = None,
        enable_thinking: bool = True,
        response_format_type: str = "text",
    ):
        """流式调用模型"""
        logger.info(f"调用流式模型，model_key: {model_key}，chats: {str(chats)}")
        messages = self._convert_chats_to_messages(chats)
        model_config = app_config.get_model_config(model_key)
        provider = self._get_provider(model_config["api"])

        try:
            last_response = None
            for response in provider.stream_call(
                model=model_config["id"],
                messages=messages,
                tools=tools,
                enable_thinking=enable_thinking,
                response_format_type=response_format_type,
            ):
                self._validate_response(response)
                last_response = response
                yield response
            logger.info(f"流式调用完成，model_key: {model_key}，response: {str(last_response)}")
        except Exception:
            logger.exception(f"流式调用失败，model_key: {model_key}")
            raise


model_caller = ModelCaller()
