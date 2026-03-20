"""钩子抽象基类和点位定义"""

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.entities import ModelConfig

T = TypeVar("T")


class BaseHook(ABC, Generic[T]):
    """钩子抽象基类，入参出参同类型"""

    order: ClassVar[int] = 100  # 执行顺序，数值越小越先执行，默认靠后

    @abstractmethod
    def execute(self, data: T | None, context: AgentContext) -> T | None:
        """执行钩子逻辑

        Args:
            data: 输入数据，可能为 None
            context: Agent 执行上下文

        Returns:
            处理后的数据，可能为 None
        """
        pass


class PromptHook(BaseHook[list[Chat]]):
    """处理提示词"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        raise NotImplementedError("Subclasses must implement execute method")


class HistoryChatsHook(BaseHook[list[Chat]]):
    """处理历史对话列表"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        raise NotImplementedError("Subclasses must implement execute method")


class ModelHook(BaseHook[ModelConfig]):
    """处理模型配置，决定调用哪个模型（首个被执行的钩子）"""

    def execute(
        self, data: ModelConfig | None, context: AgentContext
    ) -> ModelConfig | None:
        """
        Args:
            data: 默认模型配置对象，可能为 None
            context: 上下文，可修改 context 相关属性

        Returns:
            最终使用的模型配置对象，可能为 None
        """
        raise NotImplementedError("Subclasses must implement execute method")


class ConfirmedChatHook(BaseHook[list[Chat]]):
    """处理已确认的新增对话列表"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        raise NotImplementedError("Subclasses must implement execute method")
