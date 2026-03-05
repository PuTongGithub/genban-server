"""异步任务执行器"""

import asyncio
import threading
import weakref
from typing import Optional, Callable, Any, List


class AsyncExecutor:
    """在独立线程中运行事件循环，支持线程安全任务提交和优雅停机"""

    # 全局活跃执行器列表（弱引用自动清理）
    _executors: weakref.WeakSet = weakref.WeakSet()

    def __init__(
        self, name: Optional[str] = None, on_stop: Optional[Callable[[], None]] = None
    ):
        """创建并启动执行器"""
        self._name = name or "AsyncExecutor"
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, name=self._name, daemon=True
        )
        self._stop_handlers: List[Callable[[], None]] = []

        if on_stop:
            self._stop_handlers.append(on_stop)

        self._thread.start()
        AsyncExecutor._executors.add(self)

    @classmethod
    def get_all_executors(cls) -> List["AsyncExecutor"]:
        """获取所有活跃执行器"""
        return list(cls._executors)

    @classmethod
    def stop_all(cls, timeout: Optional[float] = None) -> None:
        """停止所有执行器（全局优雅停机）"""
        for executor in cls.get_all_executors():
            try:
                executor.stop(timeout)
            except Exception:
                pass

    def _run_loop(self) -> None:
        """在线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro) -> Any:
        """提交协程到事件循环执行"""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self, timeout: Optional[float] = None) -> None:
        """停止执行器"""
        for handler in self._stop_handlers:
            try:
                handler()
            except Exception:
                pass

        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=timeout)
        AsyncExecutor._executors.discard(self)

    def is_running(self) -> bool:
        """检查执行器是否运行中"""
        return self._thread.is_alive()
