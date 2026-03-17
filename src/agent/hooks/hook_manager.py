"""钩子执行管理器"""

from typing import TypeVar, Type, Any

from src.agent.hooks.base_hook import BaseHook
from src.agent.hooks.hook_registry import HookRegistry
from src.agent.entities import AgentContext
from src.common.async_executor import AsyncExecutor

T = TypeVar("T")


class HookManager:
    """钩子执行管理器，负责执行各类钩子"""

    def __init__(self, user_id: str, registry: HookRegistry | None = None) -> None:
        self._registry = registry or HookRegistry()
        self._async_executor = AsyncExecutor(name=f"HookManagerExecutor_{user_id}")

    def register(self, hook: BaseHook) -> None:
        """注册钩子"""
        self._registry.register(hook)

    def execute(
        self, hook_type: Type[BaseHook[T]], data: T | None, context: AgentContext
    ) -> T | None:
        """同步执行指定类型的所有钩子"""
        hooks = self._registry.get_hooks(hook_type)
        for hook in hooks:
            data = hook.execute(data, context)
        return data

    def async_execute(
        self, hook_type: Type[BaseHook[T]], data: T | None, context: AgentContext
    ) -> Any:
        """异步执行指定类型的所有钩子

        使用 AsyncExecutor 在线程池中异步执行
        """

        async def _execute_async(initial_data: T | None, ctx: AgentContext) -> T | None:
            hooks = self._registry.get_hooks(hook_type)
            result = initial_data
            for hook in hooks:
                result = hook.execute(result, ctx)
            return result

        return self._async_executor.submit(_execute_async(data, context))

    def stop(self, timeout: float | None = None) -> None:
        """停止异步执行器"""
        self._async_executor.stop(timeout)
