"""模型相关的实体定义"""

from dataclasses import dataclass

from src.agent.entities import Message


@dataclass
class ModelCallOptions:
    """模型调用选项参数"""

    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    repetition_penalty: float | None = None
    response_format_type: str | None = None


@dataclass
class CallResponse:
    """大模型接口调用返回值统一封装"""

    request_id: str
    status_code: int
    total_tokens: int
    input_tokens: int
    output_tokens: int
    finish_reason: str
    message: Message
