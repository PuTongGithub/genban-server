from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, StrEnum, unique
from typing import TYPE_CHECKING

from src.agent.hooks.entities import ModelConfig
from src.common.utils import time_util

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

    def to_dict(self) -> dict:
        """将 Message 对象转换为字典"""
        return {
            "role": self.role,
            "content": self.content,
            "reasoning_content": self.reasoning_content,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Message:
        """从字典创建 Message 对象"""
        return cls(
            role=data.get("role", ""),
            content=data.get("content", []),
            reasoning_content=data.get("reasoning_content", ""),
            tool_calls=data.get("tool_calls"),
            tool_call_id=data.get("tool_call_id"),
        )


@unique
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# agent模块针对对话内容的封装
@dataclass
class Chat:
    type: str = ""  # 对话类型，参考 ChatType 枚举
    id: str = ""  # 对话id，唯一键，升序排列
    time: int = field(default_factory=time_util.get_timestamp)  # 对话时间，秒级时间戳
    message: Message = field(default_factory=Message)  # 对话内容

    def to_dict(self) -> dict:
        """将 Chat 对象转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "time": self.time,
            "message": self.message.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Chat:
        """从字典创建 Chat 对象"""
        message_data = data.get("message", {})
        return cls(
            id=data.get("id", ""),
            type=data.get("type", ""),
            time=data.get("time", 0),
            message=Message.from_dict(message_data),
        )


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
