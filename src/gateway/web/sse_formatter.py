"""SSE 格式化工具类"""

import json
from typing import Any

from src.agent.entities import Chat


class SSEFormatter:
    """将内部对象格式化为 SSE 格式的工具类（单例模式）"""

    def format_chat_to_sse(self, chat: Chat) -> str:
        """将 Chat 格式化为 SSE 格式

        Args:
            chat: Chat 对象

        Returns:
            SSE 格式的字符串
        """
        tool_calls = None
        if chat.message.tool_calls:
            tool_calls = [tc.to_dict() for tc in chat.message.tool_calls]

        data: dict[str, Any] = {
            "id": chat.id,
            "type": chat.type,
            "time": chat.time,
            "content": chat.get_cleaned_message_content(),
            "reasoning_content": chat.message.reasoning_content,
            "tool_calls": tool_calls,
            "channel_type": chat.extra.channel_type if chat.extra else "",
        }

        # SSE 格式: event: message\ndata: {...}\n\n
        return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    def format_close_signal(self) -> str:
        """格式化 SSE 关闭信号

        Returns:
            SSE 关闭信号格式的字符串
        """
        return "event: close\ndata: {}\n\n"

    def format_complete_signal(self) -> str:
        """格式化 SSE 完成信号

        Returns:
            SSE 完成信号格式的字符串
        """
        return "event: complete\ndata: {}\n\n"


# 全局单例（模块加载时初始化）
sse_formatter = SSEFormatter()
