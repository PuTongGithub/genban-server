"""通用消息管道模块"""

import queue
from typing import Generic, TypeVar

from src.common.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class MessagePipe(Generic[T]):
    """通用消息管道，支持任意类型的消息传递

    特性：
    - 泛型支持：可指定任意消息类型
    - 批量操作：支持单条和批量消息发送/接收
    - 阻塞/非阻塞：灵活的消费模式
    """

    def __init__(
        self,
        name: str,
        maxsize: int = 0,
    ) -> None:
        """初始化消息管道

        Args:
            name: 管道名称，用于日志标识
            maxsize: 队列最大容量，0表示无限制
        """
        self._name = name
        self._queue: queue.Queue[T] = queue.Queue(maxsize=maxsize)
        logger.debug(f"MessagePipe 已创建: {name}")

    def push(self, message: T) -> None:
        """发送消息到管道

        Args:
            message: 要发送的消息
        """
        self._queue.put(message)
        logger.debug(f"MessagePipe [{self._name}] 发送消息 {str(message)}")

    def push_batch(self, messages: list[T]) -> None:
        """批量发送消息到管道

        Args:
            messages: 要发送的消息列表
        """
        if not messages:
            return

        for message in messages:
            self._queue.put(message)
        logger.debug(
            f"MessagePipe [{self._name}] 批量发送 {len(messages)} 条消息 {str(messages)}"
        )

    def pull(self, timeout: float = 3.0) -> T | None:
        """从管道中拉取一条消息

        Args:
            timeout: 超时时间（秒），默认为 3.0 秒

        Returns:
            拉取到的消息，超时则返回 None
        """
        try:
            message = self._queue.get(timeout=timeout)
            logger.debug(f"MessagePipe [{self._name}] 拉取消息 {str(message)}")
            return message
        except queue.Empty:
            return None

    def pull_all(self, timeout: float = 3.0) -> list[T]:
        """拉取管道中所有待处理的消息

        若管道为空，则阻塞等待指定超时时间

        Args:
            timeout: 超时时间（秒），默认为 3.0 秒

        Returns:
            所有待处理的消息列表，超时仍无消息则返回空列表
        """
        results: list[T] = []

        if self._queue.empty():
            message = self.pull(timeout=timeout)
            if message is None:
                return results
            results.append(message)

        while not self._queue.empty():
            try:
                message = self._queue.get_nowait()
                results.append(message)
            except queue.Empty:
                break

        logger.debug(
            f"MessagePipe [{self._name}] 拉取 {len(results)} 条消息 {str(results)}"
        )
        return results

    def is_empty(self) -> bool:
        """判断消息管道是否为空"""
        return self._queue.empty()

    def is_full(self) -> bool:
        """判断消息管道是否已满"""
        return self._queue.full()

    def size(self) -> int:
        """获取当前消息数量"""
        return self._queue.qsize()
