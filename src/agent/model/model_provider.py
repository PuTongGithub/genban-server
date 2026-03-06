"""模型提供者接口定义"""

from abc import ABC, abstractmethod

from src.agent.entities import CallResponse


class ModelProvider(ABC):
    """模型提供者抽象基类"""

    @abstractmethod
    def call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = False,
    ) -> CallResponse:
        """同步调用模型

        Args:
            model: 模型名称
            messages: 消息列表
            tools: 工具列表
            enable_thinking: 是否启用思考模式

        Returns:
            模型调用响应
        """
        pass

    @abstractmethod
    async def stream_call(
        self,
        model: str,
        messages: list,
        tools: list | None = None,
        enable_thinking: bool = False,
    ):
        """流式调用模型

        Args:
            model: 模型名称
            messages: 消息列表
            tools: 工具列表
            enable_thinking: 是否启用思考模式

        Returns:
            流式响应迭代器
        """
        pass
