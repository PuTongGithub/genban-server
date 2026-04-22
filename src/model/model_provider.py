"""模型提供者接口定义"""

from abc import ABC, abstractmethod

from src.agent.entities import Message
from src.model.entities import CallResponse, ModelCallOptions


class ModelProvider(ABC):
    """模型提供者抽象基类"""

    @abstractmethod
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
        """同步调用模型

        Args:
            model: 模型名称
            messages: Message 对象列表
            tools: 工具列表
            enable_thinking: 是否启用思考模式
            base_url: API 服务端点地址
            api_key: API 密钥
            options: 模型调用选项参数

        Returns:
            模型调用响应
        """
        pass

    @abstractmethod
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
        """流式调用模型

        Args:
            model: 模型名称
            messages: Message 对象列表
            tools: 工具列表
            enable_thinking: 是否启用思考模式
            base_url: API 服务端点地址
            api_key: API 密钥
            options: 模型调用选项参数

        Returns:
            流式响应迭代器
        """
        pass
