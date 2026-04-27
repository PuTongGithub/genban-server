"""Assistant 模块实体定义"""

from typing import Any

from pydantic import BaseModel


class SubmitRequest(BaseModel):
    """提交消息请求"""

    message: str
    images: list[str] | None = None
    files: list[str] | None = None  # 用户上传的文件路径列表


class SubmitResponse(BaseModel):
    """提交消息响应"""

    success: bool = False
    chat_id: str = ""  # 本次输入新增的 Chat ID
    error: str = ""


class StopResponse(BaseModel):
    """停止响应"""

    success: bool = False
    error: str = ""


class HistoryRequest(BaseModel):
    """查询历史对话请求"""

    chat_id: str | None = None  # 查询起点 chat ID，不传则返回最新的 count 条
    chat_time: int | None = None  # 查询起点时间戳（秒级），用于路由文件
    count: int = 20  # 查询数量，默认 20


class HistoryChatItem(BaseModel):
    """历史对话条目"""

    id: str
    type: str
    time: int
    content: list[dict[str, Any]]
    reasoning_content: str = ""
    tool_calls: list[dict[str, Any]] | None = None
    channel_type: str = ""  # 消息渠道类型


class HistoryResponse(BaseModel):
    """查询历史对话响应"""

    success: bool = True
    chats: list[HistoryChatItem] = []
    total: int = 0
    error: str = ""
