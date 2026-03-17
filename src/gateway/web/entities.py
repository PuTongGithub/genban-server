"""Assistant 模块实体定义"""

from pydantic import BaseModel


class SubmitRequest(BaseModel):
    """提交消息请求"""

    message: str


class SubmitResponse(BaseModel):
    """提交消息响应"""

    success: bool = False
    chat_id: str = ""  # 本次输入新增的 Chat ID
    error: str = ""


class StopResponse(BaseModel):
    """停止响应"""

    success: bool = False
    chat_id: str = ""  # 本次停止消息的 Chat ID
    error: str = ""
