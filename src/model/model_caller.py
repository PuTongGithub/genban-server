"""模型调用器"""

from src.agent.entities import Chat, Message, ToolCall, ToolCallFunction
from src.agent.exceptions import (
    ModelCallException,
    ModelCallLengthLimitedException,
    ModelProviderNotFoundException,
)
from src.common.logger import get_logger
from src.config.config import app_config, env_config
from src.model.entities import CallResponse
from src.model.model_provider import ModelProvider
from src.model.providers.dashscope_multi_provider import DashScopeMultiProvider
from src.model.providers.dashscope_provider import DashScopeProvider
from src.model.providers.openai_provider import OpenAIProvider

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
        self._providers["openai"] = OpenAIProvider()

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
        if response.status_code != 200 or response.finish_reason == "network_error":
            raise ModelCallException(str(response))
        if response.finish_reason == "length":
            raise ModelCallLengthLimitedException()

    def _get_api_key(self, model_config: dict) -> str | None:
        """从配置中获取 API 密钥"""
        api_env_key = model_config.get("api_env_key")
        if api_env_key:
            return env_config.get(api_env_key)
        return None

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
        base_url = model_config.get("base_url")
        api_key = self._get_api_key(model_config)

        try:
            response = provider.call(
                model=model_config["id"],
                messages=messages,
                tools=tools,
                enable_thinking=enable_thinking,
                response_format_type=response_format_type,
                base_url=base_url,
                api_key=api_key,
            )
            self._validate_response(response)
            logger.info(f"模型调用成功，model_key: {model_key}，response: {str(response)}")
            return response
        except Exception:
            logger.exception(f"模型调用失败，model_key: {model_key}")
            raise

    def _accumulate_tool_calls(
        self,
        accumulated: list[ToolCall] | None,
        delta_tool_calls: list[ToolCall] | None,
    ) -> list[ToolCall] | None:
        """累积工具调用增量

        Args:
            accumulated: 已累积的工具调用列表
            delta_tool_calls: 增量的工具调用列表

        Returns:
            累积后的工具调用列表
        """
        if delta_tool_calls is None:
            return accumulated

        if accumulated is None:
            accumulated = []

        for delta in delta_tool_calls:
            index = delta.index
            while index >= len(accumulated):
                accumulated.append(
                    ToolCall(
                        index=len(accumulated),
                        id="",
                        type="function",
                        function=ToolCallFunction(name="", arguments=""),
                    )
                )
            existing = accumulated[index]

            if delta.id:
                existing.id += delta.id
            if delta.function.name:
                existing.function.name += delta.function.name
            if delta.function.arguments:
                existing.function.arguments += delta.function.arguments

        return accumulated

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
        base_url = model_config.get("base_url")
        api_key = self._get_api_key(model_config)

        accumulated_content = ""
        accumulated_reasoning = ""
        accumulated_tool_calls: list[ToolCall] | None = None

        try:
            last_response = None
            for response in provider.stream_call(
                model=model_config["id"],
                messages=messages,
                tools=tools,
                enable_thinking=enable_thinking,
                response_format_type=response_format_type,
                base_url=base_url,
                api_key=api_key,
            ):
                self._validate_response(response)
                last_response = response

                text_content = response.message.get_text_content()
                if text_content:
                    accumulated_content += text_content

                if response.message.reasoning_content:
                    accumulated_reasoning += response.message.reasoning_content

                if response.message.tool_calls:
                    accumulated_tool_calls = self._accumulate_tool_calls(
                        accumulated_tool_calls, response.message.tool_calls
                    )

                accumulated_message = Message(
                    role=response.message.role,
                    content=[{"text": accumulated_content}] if accumulated_content else [],
                    reasoning_content=accumulated_reasoning,
                    tool_calls=accumulated_tool_calls,
                )

                accumulated_response = CallResponse(
                    request_id=response.request_id,
                    status_code=response.status_code,
                    total_tokens=response.total_tokens,
                    input_tokens=response.input_tokens,
                    output_tokens=response.output_tokens,
                    finish_reason=response.finish_reason,
                    message=accumulated_message,
                )
                yield accumulated_response
            logger.info(f"流式调用完成，model_key: {model_key}，response: {str(last_response)}")
        except Exception:
            logger.exception(f"流式调用失败，model_key: {model_key}")
            raise


model_caller = ModelCaller()
