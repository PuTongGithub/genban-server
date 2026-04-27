"""StreamManager - 管理用户 SSE 连接和消息推送"""

import asyncio
from typing import AsyncGenerator

from src.agent.entities import ContentType, chat_type_map
from src.assistant.assistant_manager import assistant_manager
from src.common.logger import get_logger
from src.common.message.message_pipe import MessagePipe
from src.common.message.message_pipe_factory import MessagePipeFactory
from src.gateway.web.sse_formatter import sse_formatter

logger = get_logger(__name__)
LISTENER_NAME = "stream_listener"


class StreamManager:
    """管理用户 SSE 连接和消息推送"""

    stream_manager = None

    @classmethod
    def get_instance(cls) -> "StreamManager":
        """获取 StreamManager 实例"""
        if cls.stream_manager is None:
            cls.stream_manager = StreamManager()
        return cls.stream_manager

    def __init__(self):
        """初始化流管理器"""
        self._stop_flag = False
        self._message_pipes: dict[str, MessagePipe] = {}

    def stop(self):
        """停止流管理器"""
        self._stop_flag = True

    def _get_message_pipe(self, user_id: str) -> MessagePipe:
        """获取用户的消息管道"""
        if user_id in self._message_pipes:
            return self._message_pipes[user_id]

        self._message_pipes[user_id] = MessagePipeFactory.create_stream_pipe(user_id)
        pipe = self._message_pipes[user_id]
        assistant_manager.register_listener(
            user_id=user_id,
            listener_name=LISTENER_NAME,
            listener=lambda content: pipe.push(content),
        )
        return pipe

    async def subscribe(self, user_id: str) -> AsyncGenerator[str, None]:
        """订阅用户的消息流，返回 SSE 格式的字符串流"""
        if self._stop_flag:
            logger.info("流管理器已停止，不允许新订阅")
            return

        try:
            pipe = self._get_message_pipe(user_id)
            count_none = 0
            while True:
                # 等待新消息（使用 to_thread 避免阻塞事件循环）
                content = await asyncio.to_thread(pipe.pull)
                if content is None:
                    if count_none >= 5:
                        yield sse_formatter.format_close_signal()
                        break
                    else:
                        count_none += 1
                        continue

                count_none = 0
                # 检查消息类型
                if content.type == ContentType.COMPLETE:
                    # complete 事件直接输出
                    yield sse_formatter.format_complete_signal()
                elif content.type == ContentType.CHAT:
                    # chat 事件需要检查 user_visible
                    chats = content.chat
                    if chats is None:
                        continue
                    for chat in chats:
                        chat_type = chat_type_map[chat.type]
                        if not chat_type.user_visible:
                            continue
                        # 格式化为 SSE 格式
                        event_data = sse_formatter.format_chat_to_sse(chat)
                        yield event_data

        except asyncio.CancelledError:
            # 客户端断开连接
            logger.info(f"用户 {user_id} 已断开 SSE 连接")
