from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, StrEnum, unique
from modulefinder import test

from src.agent.hooks.entities import ModelConfig
from src.common.utils import time_util


@dataclass
class ToolCallFunction:
    """工具调用函数定义"""

    name: str = ""
    arguments: str = ""

    def to_dict(self) -> dict:
        """将 ToolCallFunction 对象转换为字典"""
        return {
            "name": self.name,
            "arguments": self.arguments,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ToolCallFunction:
        """从字典创建 ToolCallFunction 对象"""
        return cls(
            name=data.get("name", ""),
            arguments=data.get("arguments", ""),
        )


@dataclass
class ToolCall:
    """工具调用定义"""

    index: int = 0
    id: str = ""
    type: str = "function"
    function: ToolCallFunction = field(default_factory=ToolCallFunction)

    def to_dict(self) -> dict:
        """将 ToolCall 对象转换为字典"""
        return {
            "index": self.index,
            "id": self.id,
            "type": self.type,
            "function": self.function.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> ToolCall:
        """从字典创建 ToolCall 对象"""
        func_data = data.get("function", {})
        return cls(
            index=data.get("index", 0),
            id=data.get("id", ""),
            type=data.get("type", "function"),
            function=ToolCallFunction.from_dict(func_data),
        )


# 大模型消息实体
@dataclass
class Message:
    role: str = ""  # 角色类型，参考 MessageRole 枚举
    content: list = field(default_factory=list)  # 内容统一为列表格式，纯文本为 [{"text": "内容"}]
    reasoning_content: str = ""
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None  # 工具调用id，仅作为大模型调用入参时使用

    def to_dict(self) -> dict:
        """将 Message 对象转换为字典"""
        return {
            "role": self.role,
            "content": self.content,
            "reasoning_content": self.reasoning_content,
            "tool_calls": [tc.to_dict() for tc in self.tool_calls] if self.tool_calls else None,
            "tool_call_id": self.tool_call_id,
        }

    def get_text_contents(self) -> list[str]:
        """提取消息中的所有文本内容"""
        text_parts: list[str] = []
        for item in self.content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return text_parts

    def get_text_content(self) -> str:
        """提取消息中的文本内容"""
        text_parts = self.get_text_contents()
        return "".join(text_parts)

    @classmethod
    def from_dict(cls, data: dict) -> Message:
        """从字典创建 Message 对象"""
        tool_calls_data = data.get("tool_calls")
        tool_calls = None
        if tool_calls_data:
            tool_calls = [ToolCall.from_dict(tc) for tc in tool_calls_data]
        return cls(
            role=data.get("role", ""),
            content=data.get("content", []),
            reasoning_content=data.get("reasoning_content", ""),
            tool_calls=tool_calls,
            tool_call_id=data.get("tool_call_id"),
        )


@unique
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class ChatExtra:
    channel_type: str | None = None  # 渠道类型，参考 BaseIMChannel.channel_type

    def to_dict(self) -> dict:
        """将 ChatExtra 对象转换为字典"""
        result = {}
        if self.channel_type:
            result["channel_type"] = self.channel_type
        return result

    @classmethod
    def from_dict(cls, data: dict | None) -> ChatExtra | None:
        """从字典创建 ChatExtraData 对象"""
        if data is None:
            return None
        return cls(
            channel_type=data.get("channel_type"),
        )


# agent模块针对对话内容的封装
@dataclass
class Chat:
    type: str = ""  # 对话类型，参考 ChatType 枚举
    id: str = ""  # 对话id，唯一键，升序排列
    time: int = field(default_factory=time_util.get_timestamp)  # 对话时间，秒级时间戳
    message: Message = field(default_factory=Message)  # 对话内容
    extra: ChatExtra | None = None  # 额外数据，用于存储额外信息

    def to_dict(self) -> dict:
        """将 Chat 对象转换为字典"""
        result = {
            "id": self.id,
            "type": self.type,
            "time": self.time,
            "message": self.message.to_dict(),
        }
        if self.extra:
            result["extra"] = self.extra.to_dict()
        return result

    def get_cleaned_message_content_text(self) -> str:
        """获取清理后的消息文本，移除文本项开头的 [] 包裹内容

        Returns:
            清理后的文本内容
        """
        cleaned_content = self.get_cleaned_message_content()
        text = ""
        for item in cleaned_content:
            if isinstance(item, dict) and "text" in item:
                text += item["text"]
        return text

    def get_cleaned_message_content(self) -> list:
        """获取清理后的消息内容，移除文本项开头的 [] 包裹内容

        Returns:
            清理后的内容列表
        """
        chat_type = chat_type_map[self.type]
        if not chat_type.message_with_tag:
            return self.message.content

        cleaned_content = []
        for item in self.message.content:
            if isinstance(item, dict) and "text" in item:
                text = item["text"]
                if text and text.startswith("["):
                    cleaned_text = re.sub(r"^\[[^\]]*\]", "", text)
                    cleaned_content.append({"text": cleaned_text})
            else:
                cleaned_content.append(item)
        return cleaned_content

    @classmethod
    def from_dict(cls, data: dict) -> Chat:
        """从字典创建 Chat 对象"""
        message_data = data.get("message", {})
        extra_data = data.get("extra")
        return cls(
            type=data.get("type", ""),
            id=data.get("id", ""),
            time=data.get("time", 0),
            message=Message.from_dict(message_data),
            extra=ChatExtra.from_dict(extra_data),
        )


@dataclass
class ChatTypeInfo:
    type: str = ""
    user_visible: bool = False
    assistant_visible: bool = False
    message_with_tag: bool = False


@unique
class ChatType(ChatTypeInfo, Enum):
    DEFAULT = ("default", False, False, False)
    PROMPT = ("prompt", False, True, False)
    SYSTEM_REMAINDER = ("system_remainder", False, True, True)
    SKILL_PROMPT = ("skill_prompt", False, True, True)
    SCHEDULE = ("schedule", False, True, True)
    SCHEDULE_REMINDER = ("schedule_reminder", True, True, True)
    CONVERSATION = ("conversation", False, True, True)
    USER = ("user", True, True, True)
    ASSISTANT = ("assistant", True, True, False)
    TOOL = ("tool", True, True, False)
    MEMORY = ("memory", False, True, True)
    ERROR = ("error", True, True, True)
    STOP = ("stop", True, True, True)  # 停止消息，用于中断 Agent 执行


chat_type_map = {chatType.type: chatType for chatType in ChatType}


# Agent 单次执行上下文
@dataclass
class AgentContext:
    user_id: str = ""  # 用户 ID
    model_config: ModelConfig | None = None  # model_hook 结果：当前使用的模型配置
    prompt_chats: list[Chat] = field(default_factory=list)  # prompt_hook 结果：处理后的提示词列表
    history_chats: list[Chat] = field(default_factory=list)  # chats_hook 结果：处理后的历史对话列表
    new_chats: list[Chat] = field(default_factory=list)  # 本次新增的 Chat 列表
    total_tokens: int = 0  # 当前对话的总 token 数
    process_result: bool = False  # _process_contents 的返回值，表示本轮对话是否完成


@unique
class ContentType(StrEnum):
    """消息管道内容类型"""

    CHAT = "chat"
    COMPLETE = "complete"


@dataclass
class MessagePipeContent:
    """消息管道实体"""

    chat: Chat | None = None
    type: ContentType = ContentType.CHAT
