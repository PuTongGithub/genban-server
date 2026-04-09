"""异步任务执行器"""

import asyncio
import threading
import weakref
from typing import Any, Callable, List, Optional

from src.common.logger import get_logger

logger = get_logger(__name__)


class AsyncExecutor:
    """在独立线程中运行事件循环，支持线程安全任务提交和优雅停机"""

    # 全局活跃执行器列表（弱引用自动清理）
    _executors: weakref.WeakSet = weakref.WeakSet()

    @classmethod
    def get_all_executors(cls) -> List["AsyncExecutor"]:
        """获取所有活跃执行器"""
        return list(cls._executors)

    @classmethod
    def stop_all(cls, timeout: Optional[float] = None) -> None:
        """停止所有执行器（全局优雅停机）"""
        logger.info(f"正在停止所有 AsyncExecutor，数量: {len(cls.get_all_executors())}")
        for executor in cls.get_all_executors():
            try:
                executor.stop(timeout)
            except Exception:
                logger.exception(f"停止 AsyncExecutor 失败: {executor._name}")

    def __init__(self, name: Optional[str] = None, on_stop: Optional[Callable[[], None]] = None):
        """创建并启动执行器"""
        self._name = name or "AsyncExecutor"
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, name=self._name, daemon=True)
        self._stop_handlers: List[Callable[[], None]] = []

        if on_stop:
            self._stop_handlers.append(on_stop)

        self._thread.start()
        self._running = True
        AsyncExecutor._executors.add(self)
        logger.debug(f"AsyncExecutor 已创建: {self._name}")

    def _run_loop(self) -> None:
        """在线程中运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def is_running(self) -> bool:
        """检查执行器是否运行中"""
        return self._running

    def submit(self, coro) -> Any:
        """提交协程到事件循环执行"""
        if not self._running:
            logger.warning(f"AsyncExecutor {self._name} 未运行，无法提交任务")
            return
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self, timeout: Optional[float] = None) -> None:
        """停止执行器"""
        if not self._running:
            return
        logger.debug(f"正在停止 AsyncExecutor: {self._name}")
        self._running = False

        # 先执行停止处理器（让任务有机会正常退出）
        for handler in self._stop_handlers:
            try:
                handler()
            except Exception:
                logger.exception(f"执行停止处理器失败: {self._name}")

        # 取消所有待处理的任务
        def cancel_all_tasks():
            """取消事件循环中的所有任务"""
            tasks = [t for t in asyncio.all_tasks(self._loop) if not t.done()]
            if tasks:
                logger.debug(f"取消 {len(tasks)} 个待处理任务")
                for task in tasks:
                    task.cancel()

        # 在事件循环中执行取消操作
        self._loop.call_soon_threadsafe(cancel_all_tasks)

        # 给任务一点时间响应取消
        import time
        time.sleep(0.1)

        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=timeout)
        AsyncExecutor._executors.discard(self)
        logger.debug(f"AsyncExecutor 已停止: {self._name}")
