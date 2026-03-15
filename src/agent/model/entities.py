"""模型相关的实体定义"""

from dataclasses import dataclass

from src.agent.entities import Message


@dataclass
class CallResponse:
    """大模型接口调用返回值统一封装"""

    request_id: str
    status_code: int
    total_tokens: int
    finish_reason: str
    message: Message
