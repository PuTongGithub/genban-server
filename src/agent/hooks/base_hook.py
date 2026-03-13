"""钩子抽象基类和点位定义"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.agent.entities import Chat, AgentContext, ModelConfig
from src.agent.tools.tool_registry import ToolRegistry

T = TypeVar("T")


class BaseHook(ABC, Generic[T]):
    """钩子抽象基类，入参出参同类型"""

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


class ChatHook(BaseHook[Chat]):
    """处理单个对话"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        raise NotImplementedError("Subclasses must implement execute method")


class PromptHook(BaseHook[list[Chat]]):
    """处理提示词"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        raise NotImplementedError("Subclasses must implement execute method")


class ChatsHook(BaseHook[list[Chat]]):
    """处理对话列表"""

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


class ToolsHook(BaseHook[ToolRegistry]):
    """处理工具注册表"""

    def execute(
        self, data: ToolRegistry | None, context: AgentContext
    ) -> ToolRegistry | None:
        raise NotImplementedError("Subclasses must implement execute method")


class NewChatHook(BaseHook[Chat]):
    """处理新对话"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        raise NotImplementedError("Subclasses must implement execute method")


class CompleteHook(BaseHook[list[Chat]]):
    """处理完成对话"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        raise NotImplementedError("Subclasses must implement execute method")
