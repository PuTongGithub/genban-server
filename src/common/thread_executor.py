"""线程任务执行器"""

import threading
import weakref
from typing import Optional, Callable, List

from src.common.logger import get_logger

logger = get_logger(__name__)


class ThreadExecutor:
    """在线程中运行循环任务，支持线程安全任务提交和优雅停机"""

    _executors: weakref.WeakSet = weakref.WeakSet()

    @classmethod
    def get_all_executors(cls) -> List["ThreadExecutor"]:
        """获取所有活跃执行器"""
        return list(cls._executors)

    @classmethod
    def stop_all(cls, timeout: Optional[float] = None) -> None:
        """停止所有执行器（全局优雅停机）"""
        logger.info(
            f"正在停止所有 ThreadExecutor，数量: {len(cls.get_all_executors())}"
        )
        for executor in cls.get_all_executors():
            try:
                executor.stop(timeout)
            except Exception:
                logger.exception(f"停止 ThreadExecutor 失败: {executor._name}")

    def __init__(
        self,
        target: Callable[[], None],
        kwargs: dict = {},
        name: Optional[str] = None,
        on_stop: Optional[Callable[[], None]] = None,
    ):
        """创建并启动执行器

        Args:
            target: 要在线程中运行的循环函数
            name: 执行器名称
            on_stop: 停止时执行的回调函数
        """
        self._name = name or "ThreadExecutor"
        self._target = target
        self._thread = threading.Thread(
            target=self._run_loop, name=self._name, daemon=True, kwargs=kwargs
        )
        self._stop_handlers: List[Callable[[], None]] = []
        self._stop_event = threading.Event()

        if on_stop:
            self._stop_handlers.append(on_stop)

        ThreadExecutor._executors.add(self)
        logger.debug(f"ThreadExecutor 已创建: {self._name}")

    def _run_loop(self) -> None:
        """在线程中运行目标函数"""
        try:
            self._target()
        except Exception:
            logger.exception(f"ThreadExecutor {self._name} 执行目标函数时发生异常")

    def start(self) -> None:
        """启动执行器"""
        if self._stop_event.is_set():
            self._stop_event.clear()
        self._thread.start()
        logger.debug(f"ThreadExecutor 已启动: {self._name}")

    def is_running(self) -> bool:
        """检查执行器是否运行中"""
        return not self._stop_event.is_set()

    def stop(self, timeout: Optional[float] = None) -> None:
        """停止执行器"""
        if self._stop_event.is_set():
            return
        logger.debug(f"正在停止 ThreadExecutor: {self._name}")
        self._stop_event.set()
        for handler in self._stop_handlers:
            try:
                handler()
            except Exception:
                logger.exception(f"执行停止处理器失败: {self._name}")

        self._thread.join(timeout=timeout)
        ThreadExecutor._executors.discard(self)
        logger.debug(f"ThreadExecutor 已停止: {self._name}")
