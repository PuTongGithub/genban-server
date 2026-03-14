from dataclasses import dataclass, field
from enum import StrEnum, unique, Enum
from typing import Any

from src.common.utils import time_util


# 大模型消息实体
@dataclass
class Message:
    role: str = ""  # 角色: system, user, assistant, tool
    content: list = field(default_factory=list)  # 内容统一为列表格式，纯文本为 [{"text": "内容"}]
    reasoning_content: str = ""
    tool_calls: list | None = None
    tool_call_id: str | None = None


@unique
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# 大模型接口调用返回值统一封装
@dataclass
class CallResponse:
    request_id: str
    status_code: int
    total_tokens: int
    finish_reason: str
    message: Message


# agent模块针对对话内容的封装
@dataclass
class Chat:
    type: str = (
        ""  # 对话类型: prompt, user, assistant, tool, command, memory, toolSummary
    )
    id: str = ""  # 对话id，唯一键，升序排列
    time: int = field(default_factory=time_util.get_timestamp)  # 对话时间，秒级时间戳
    total_tokens: int = 0  # 本次调用消耗的token数（仅source=assistant时有效）
    message: Message = field(default_factory=Message)  # 对话内容


@dataclass
class ChatTypeInfo:
    type: str = ""
    userVisible: bool = False
    assistantVisible: bool = False
    messageWithTag: bool = False


@unique
class ChatType(ChatTypeInfo, Enum):
    PROMPT = ("prompt", False, True, False)
    SYSTEM_REMAINDER = ("system_remainder", False, True, True)
    USER = ("user", False, True, True)
    ASSISTANT = ("assistant", True, True, False)
    TOOL = ("tool", True, True, False)
    COMMAND = ("command", True, False, False)
    MEMORY = ("memory", False, True, True)
    ERROR = ("error", True, True, False)


chatTypeMap = {chatType.type: chatType for chatType in ChatType}


# 模型配置
@dataclass
class ModelConfig:
    """模型配置"""

    model_key: str = ""  # 模型 key
    enable_thinking: bool = False  # 是否启用思考模式


# Agent 单次执行上下文
@dataclass
class AgentContext:
    model_config: ModelConfig | None = None  # model_hook 结果：当前使用的模型配置
    user_id: str = ""  # 用户 ID
    input_chat: Chat = field(default_factory=Chat)  # 本次 Agent.run 传入的 Chat
    prompt_chats: list[Chat] = field(
        default_factory=list
    )  # prompt_hook 结果：处理后的提示词列表
    history_chats: list[Chat] = field(
        default_factory=list
    )  # chats_hook 结果：处理后的历史对话列表
    new_chats: list[Chat] = field(
        default_factory=list
    )  # 新增的 Chat 列表（用于收集本次所有新增对话）


# 工具相关的数据结构定义
@dataclass
class ToolParameter:
    """工具参数定义"""

    name: str
    type: str
    description: str
    required: bool = True
    enum: list | None = None


@dataclass
class ToolCall:
    """工具调用定义"""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ToolResult:
    """工具执行结果"""

    tool_call_id: str
    content: str
