"""钩子执行管理器"""

from typing import Any, Type, TypeVar

from src.agent.entities import AgentContext
from src.agent.hooks.base_hook import BaseHook
from src.agent.hooks.hook_registry import HookRegistry
from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class HookManager:
    """钩子执行管理器，负责执行各类钩子"""

    def __init__(self, user_id: str, registry: HookRegistry | None = None) -> None:
        self._registry = registry or HookRegistry()
        self._async_executor = AsyncExecutor(name=f"HookManagerExecutor_{user_id}")

    def register(self, hook: BaseHook) -> None:
        """注册钩子"""
        self._registry.register(hook)

    def _execute_hooks(
        self,
        hook_type: Type[BaseHook[T]],
        initial_data: T | None,
        context: AgentContext,
    ) -> T | None:
        """执行指定类型的所有钩子，统一处理异常"""
        hooks = self._registry.get_hooks(hook_type)
        result = initial_data
        for hook in hooks:
            try:
                result = hook.execute(result, context)
            except Exception:
                logger.exception(
                    f"钩子执行失败: hook={hook.__class__.__name__}, type={hook_type.__name__}"
                )
        return result

    def execute(
        self, hook_type: Type[BaseHook[T]], data: T | None, context: AgentContext
    ) -> T | None:
        """同步执行指定类型的所有钩子"""
        return self._execute_hooks(hook_type, data, context)

    def async_execute(
        self, hook_type: Type[BaseHook[T]], data: T | None, context: AgentContext
    ) -> Any:
        """异步执行指定类型的所有钩子

        使用 AsyncExecutor 在线程池中异步执行
        """

        async def _execute_async(initial_data: T | None, ctx: AgentContext) -> T | None:
            return self._execute_hooks(hook_type, initial_data, ctx)

        return self._async_executor.submit(_execute_async(data, context))

    def stop(self, timeout: float | None = None) -> None:
        """停止异步执行器"""
        self._async_executor.stop(timeout)
