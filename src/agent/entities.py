from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum, unique, Enum
from typing import TYPE_CHECKING

from src.common.utils import time_util
from src.agent.hooks.entities import ModelConfig

if TYPE_CHECKING:
    from src.modules.base_module import BaseModule


# 大模型消息实体
@dataclass
class Message:
    role: str = ""  # 角色类型，参考 MessageRole 枚举
    content: list = field(
        default_factory=list
    )  # 内容统一为列表格式，纯文本为 [{"text": "内容"}]
    reasoning_content: str = ""
    tool_calls: list | None = None
    tool_call_id: str | None = None


@unique
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# Token使用统计
@dataclass
class Usage:
    total_tokens: int = 0  # 本次调用消耗的总token数
    input_tokens: int = 0  # 输入token数
    output_tokens: int = 0  # 输出token数


# agent模块针对对话内容的封装
@dataclass
class Chat:
    type: str = ""  # 对话类型，参考 ChatType 枚举
    id: str = ""  # 对话id，唯一键，升序排列
    time: int = field(default_factory=time_util.get_timestamp)  # 对话时间，秒级时间戳
    usage: Usage = field(default_factory=Usage)  # Token使用统计
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
    USER = ("user", True, True, True)
    ASSISTANT = ("assistant", True, True, False)
    TOOL = ("tool", True, True, False)
    MEMORY = ("memory", False, True, True)
    ERROR = ("error", True, True, True)
    STOP = ("stop", True, True, True)  # 停止消息，用于中断 Agent 执行


chatTypeMap = {chatType.type: chatType for chatType in ChatType}


# Agent 单次执行上下文
@dataclass
class AgentContext:
    user_id: str = ""  # 用户 ID
    model_config: ModelConfig | None = None  # model_hook 结果：当前使用的模型配置
    prompt_chats: list[Chat] = field(
        default_factory=list
    )  # prompt_hook 结果：处理后的提示词列表
    history_chats: list[Chat] = field(
        default_factory=list
    )  # chats_hook 结果：处理后的历史对话列表
    new_chats: list[Chat] = field(default_factory=list)  # 本次新增的 Chat 列表
    modules: list["BaseModule"] = field(
        default_factory=list
    )  # 已注册的模块列表，供钩子访问


@dataclass
class MessagePipeContent:
    """消息管道实体"""

    chat: Chat
