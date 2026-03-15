"""钩子注册中心"""

from typing import TypeVar

from src.agent.hooks.base_hook import BaseHook

T = TypeVar("T")


class HookRegistry:
    """钩子注册中心，管理所有钩子的注册"""

    def __init__(self) -> None:
        self._registry: dict[type[BaseHook], list[BaseHook]] = {}

    def register(self, hook: BaseHook) -> None:
        """注册钩子，自动识别所有实现的点位类型

        Args:
            hook: 钩子实例
        """
        for hook_type in type(hook).__mro__:
            if hook_type == BaseHook:
                break
            if issubclass(hook_type, BaseHook):
                if hook_type not in self._registry:
                    self._registry[hook_type] = []
                self._registry[hook_type].append(hook)

    def get_hooks(self, hook_type: type[BaseHook[T]]) -> list[BaseHook[T]]:
        """获取指定类型的所有钩子，按 order 排序

        Args:
            hook_type: 钩子类型

        Returns:
            按 order 排序后的钩子实例列表
        """
        hooks = self._registry.get(hook_type, [])
        return sorted(hooks, key=lambda h: type(h).order)
