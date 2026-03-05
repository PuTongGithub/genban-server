"""模型调用器"""

from src.config.config import app_config
from src.agent.model.model_provider import ModelProvider
from src.agent.model.providers.dashscope_provider import DashScopeProvider
from src.agent.exceptions import (
    ModelProviderNotFoundException,
    ModelCallLengthLimitedException,
    ModelCallException,
)
from src.agent.entities import CallResponse, Chat, Message
from src.agent.chat_factory import chat_factory


class ModelCaller:
    """模型调用器，统一封装不同 Provider 的调用"""

    def __init__(self) -> None:
        self._providers: dict[str, ModelProvider] = {}
        self._register_default_providers()

    def _register_default_providers(self) -> None:
        """注册默认的模型提供者"""
        self._providers["dashscope"] = DashScopeProvider()

    def _get_provider(self, api_name: str) -> ModelProvider:
        """获取模型提供者"""
        if api_name not in self._providers:
            raise ModelProviderNotFoundException(f"provider:{api_name}")
        return self._providers[api_name]

    def _convert_chats_to_messages(self, chats: list[Chat]) -> list[dict]:
        """将 Chat 列表转换为模型调用所需的消息格式"""
        messages: list[dict] = []
        for chat in chats:
            msg = self._convert_message_to_dict(chat.message)
            if msg:
                messages.append(msg)
        return messages

    def _convert_message_to_dict(self, message: Message) -> dict | None:
        """将 Message 转换为字典格式"""
        if not message.role:
            return None

        msg_dict: dict = {
            "role": message.role,
            "content": message.content,
        }

        if message.tool_calls:
            msg_dict["tool_calls"] = message.tool_calls

        if message.tool_call_id:
            msg_dict["tool_call_id"] = message.tool_call_id

        return msg_dict

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
        enable_thinking: bool = False,
    ) -> Chat:
        """调用模型"""
        messages = self._convert_chats_to_messages(chats)
        model_config = app_config.get_model_config(model_key)
        provider = self._get_provider(model_config["api"])
        response = provider.call(
            model=model_config["id"],
            messages=messages,
            tools=tools,
            enable_thinking=enable_thinking,
        )
        self._validate_response(response)
        return chat_factory.create_assistant_chat(response)

    def stream_call(
        self,
        model_key: str,
        chats: list[Chat],
        tools: list | None = None,
        enable_thinking: bool = False,
    ):
        """流式调用模型"""
        messages = self._convert_chats_to_messages(chats)
        model_config = app_config.get_model_config(model_key)
        provider = self._get_provider(model_config["api"])
        for response in provider.stream_call(
            model=model_config["id"],
            messages=messages,
            tools=tools,
            enable_thinking=enable_thinking,
        ):
            self._validate_response(response)
            yield chat_factory.create_assistant_chat(response)


model_caller = ModelCaller()
