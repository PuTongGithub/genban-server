"""钩子执行管理器"""

from typing import Type, TypeVar

from src.agent.entities import AgentContext
from src.agent.hooks.base_hook import BaseHook
from src.agent.hooks.hook_registry import HookRegistry
from src.common.thread_pool_executor import ThreadPoolExecutor
from src.common.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class HookManager:
    """钩子执行管理器，负责执行各类钩子"""

    def __init__(self, user_id: str, registry: HookRegistry | None = None) -> None:
        self._registry = registry or HookRegistry()
        self._async_executor = ThreadPoolExecutor(name=f"HookManagerExecutor_{user_id}", max_workers=10)

    def register(self, hook: BaseHook) -> None:
        """注册钩子"""
        self._registry.register(hook)
    
    def _execute_hook_sync(self, hook: BaseHook, initial_data: T | None, ctx: AgentContext) -> T | None:
        """同步执行指定钩子"""
        try:
            return hook.execute(initial_data, ctx)
        except Exception:
            logger.exception(
                f"钩子执行失败: hook={hook.__class__.__name__}, type={hook.__class__.__name__}"
            )
            return initial_data

    async def _execute_hook_async(self, hook: BaseHook, initial_data: T | None, ctx: AgentContext):
        """异步执行指定钩子"""
        self._execute_hook_sync(hook, initial_data, ctx)

    def _execute_hooks(
        self,
        hook_type: Type[BaseHook[T]],
        initial_data: T | None,
        context: AgentContext,
    ) -> T | None:
        """执行指定类型的所有钩子，统一处理异常"""
        hooks = self._registry.get_hooks(hook_type)
        async_hooks = []
        sync_hooks = []
        for hook in hooks:
            if hook.async_execute:
                async_hooks.append(hook)
            else:
                sync_hooks.append(hook)

        # 先提交异步钩子
        for async_hook in async_hooks:
            self._async_executor.submit(self._execute_hook_sync, async_hook, initial_data, context)

        # 再执行同步钩子
        result = initial_data
        for hook in sync_hooks:
            result = self._execute_hook_sync(hook, result, context)
        return result

    def execute(
        self, hook_type: Type[BaseHook[T]], data: T | None, context: AgentContext
    ) -> T | None:
        """执行指定类型的所有钩子"""
        return self._execute_hooks(hook_type, data, context)

    def stop(self, timeout: float | None = None) -> None:
        """停止异步执行器"""
        self._async_executor.stop(timeout)
