"""StreamManager - 管理用户 SSE 连接和消息推送"""

import asyncio
from typing import AsyncGenerator, Dict

from src.agent.entities import Chat
from src.assistant.web.sse_formatter import sse_formatter


class StreamManager:
    """管理用户 SSE 连接和消息推送"""

    def __init__(self) -> None:
        # 用户 SSE 队列: {user_id: asyncio.Queue[Chat | None]}
        self._user_queues: Dict[str, asyncio.Queue[Chat | None]] = {}

    async def subscribe(self, user_id: str) -> AsyncGenerator[str, None]:
        """订阅用户的消息流，返回 SSE 格式的字符串流"""
        # 创建用户专属队列
        queue: asyncio.Queue[Chat | None] = asyncio.Queue()
        self._user_queues[user_id] = queue

        try:
            while True:
                # 等待新消息
                chat = await queue.get()
                if chat is None:
                    break

                # 格式化为 SSE 格式
                event_data = sse_formatter.format_chat_to_sse(chat)
                yield event_data

                # 标记任务完成
                queue.task_done()
        except asyncio.CancelledError:
            # 客户端断开连接
            pass
        finally:
            # 清理队列
            if user_id in self._user_queues:
                del self._user_queues[user_id]

    def push_chat(self, user_id: str, chat: Chat) -> None:
        """推送 Chat 到指定用户的 SSE 流"""
        if user_id in self._user_queues:
            queue = self._user_queues[user_id]
            try:
                # 非阻塞方式放入队列
                queue.put_nowait(chat)
            except asyncio.QueueFull:
                # 队列已满，忽略该消息
                pass

    def stop(self) -> None:
        """停止所有用户流"""
        for queue in self._user_queues.values():
            queue.put_nowait(None)


# 全局单例
stream_manager = StreamManager()
