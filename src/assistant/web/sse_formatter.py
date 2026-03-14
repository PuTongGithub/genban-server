"""SSE 格式化工具类"""

import json
import re
from typing import Any

from src.agent.entities import Chat, ChatType, chatTypeMap


class SSEFormatter:
    """将内部对象格式化为 SSE 格式的工具类（单例模式）"""

    _instance: "SSEFormatter | None" = None

    def __new__(cls) -> "SSEFormatter":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _clean_content(self, type: str, content: list) -> list:
        """根据类型清理内容，移除文本项开头的 [] 包裹内容"""
        chatType: ChatType = chatTypeMap[type]
        if not chatType.messageWithTag:
            return content

        # 处理列表中的文本项
        cleaned_content = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text = item["text"]
                # 移除开头的 [] 包裹内容
                cleaned_text = re.sub(r"^\[[^\]]*\]", "", text)
                cleaned_content.append({"text": cleaned_text})
            else:
                cleaned_content.append(item)
        return cleaned_content

    def format_chat_to_sse(self, chat: Chat) -> str:
        """将 Chat 格式化为 SSE 格式

        Args:
            chat: Chat 对象

        Returns:
            SSE 格式的字符串
        """
        data: dict[str, Any] = {
            "id": chat.id,
            "type": chat.type,
            "time": chat.time,
            "content": self._clean_content(chat.type, chat.message.content),
            "reasoning_content": chat.message.reasoning_content,
            "tool_calls": chat.message.tool_calls,
        }

        # SSE 格式: data: {...}\n\n
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


# 全局单例（模块加载时初始化）
sse_formatter = SSEFormatter()
