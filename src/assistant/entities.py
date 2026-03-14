"""Assistant 模块实体定义"""

from pydantic import BaseModel
from typing import Any

from src.agent.entities import Chat


class SubmitRequest(BaseModel):
    """提交消息请求"""

    message: str


class SubmitResponse(BaseModel):
    """提交消息响应"""

    success: bool = False
    chat_id: str = ""  # 本次输入新增的 Chat ID
    error: str = ""


class ChatEvent(BaseModel):
    """SSE 聊天事件"""

    id: str
    type: str
    time: int
    content: list  # 统一为列表格式，纯文本为 [{"text": "内容"}]
    reasoning_content: str = ""
    tool_calls: list[dict[str, Any]] | None = None


class QueueItem:
    """队列项 - 包含用户ID和Chat对象"""

    def __init__(self, user_id: str, chat: Chat):
        self.user_id = user_id
        self.chat = chat
