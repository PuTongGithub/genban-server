"""线程池执行器"""

import weakref
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor as ConcurrentThreadPoolExecutor
from typing import Callable, Iterable, List, Optional, TypeVar

from src.common.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class ThreadPoolExecutor:
    """基于 ThreadPoolExecutor 的线程池封装，支持线程安全任务提交和优雅停机"""

    _executors: weakref.WeakSet = weakref.WeakSet()

    @classmethod
    def get_all_executors(cls) -> List["ThreadPoolExecutor"]:
        """获取所有活跃执行器"""
        return list(cls._executors)

    @classmethod
    def stop_all(cls, timeout: Optional[float] = None) -> None:
        """停止所有执行器（全局优雅停机）

        Args:
            timeout: 等待任务完成的超时时间（秒），None 表示无限等待
        """
        logger.info(f"正在停止所有 ThreadPoolExecutor，数量: {len(cls.get_all_executors())}")
        for executor in cls.get_all_executors():
            try:
                executor.stop(timeout)
            except Exception:
                logger.exception(f"停止 ThreadPoolExecutor 失败: {executor._name}")

    def __init__(
        self,
        max_workers: Optional[int] = None,
        name: Optional[str] = None,
        on_stop: Optional[Callable[[], None]] = None,
    ):
        """创建并启动线程池执行器

        Args:
            max_workers: 线程池最大线程数，None 表示使用默认值
            name: 执行器名称
            on_stop: 停止时执行的回调函数
        """
        self._name = name or "ThreadPoolExecutor"
        self._max_workers = max_workers
        self._executor: Optional[ConcurrentThreadPoolExecutor] = ConcurrentThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix=f"{self._name}-"
        )
        self._stop_handlers: List[Callable[[], None]] = []
        self._running = True

        if on_stop:
            self._stop_handlers.append(on_stop)

        ThreadPoolExecutor._executors.add(self)
        logger.debug(f"ThreadPoolExecutor 已创建: {self._name}, max_workers={max_workers}")

    def submit(self, fn: Callable[..., R], *args, **kwargs) -> Future[R]:
        """提交任务到线程池执行

        Args:
            fn: 要执行的函数
            *args: 函数的位置参数
            **kwargs: 函数的关键字参数

        Returns:
            Future 对象，可用于获取执行结果

        Raises:
            RuntimeError: 线程池已停止时抛出
        """
        if not self._running or self._executor is None:
            raise RuntimeError(f"ThreadPoolExecutor {self._name} 已停止，无法提交任务")

        return self._executor.submit(fn, *args, **kwargs)

    def map(
        self, fn: Callable[[T], R], iterable: Iterable[T], timeout: Optional[float] = None
    ) -> Iterable[R]:
        """批量提交任务到线程池执行

        Args:
            fn: 要执行的函数
            iterable: 可迭代对象，每个元素作为 fn 的参数
            timeout: 每个任务的超时时间（秒）

        Returns:
            结果迭代器，按输入顺序返回结果

        Raises:
            RuntimeError: 线程池已停止时抛出
        """
        if not self._running or self._executor is None:
            raise RuntimeError(f"ThreadPoolExecutor {self._name} 已停止，无法提交任务")

        return self._executor.map(fn, iterable, timeout=timeout)

    def is_running(self) -> bool:
        """检查执行器是否运行中"""
        return self._running

    def stop(self, timeout: Optional[float] = None) -> None:
        """停止执行器

        Args:
            timeout: 等待任务完成的超时时间（秒），None 表示无限等待
        """
        if not self._running:
            return

        logger.debug(f"正在停止 ThreadPoolExecutor: {self._name}")
        self._running = False

        # 先执行停止处理器
        for handler in self._stop_handlers:
            try:
                handler()
            except Exception:
                logger.exception(f"执行停止处理器失败: {self._name}")

        # 关闭线程池
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None

        ThreadPoolExecutor._executors.discard(self)
        logger.debug(f"ThreadPoolExecutor 已停止: {self._name}")
