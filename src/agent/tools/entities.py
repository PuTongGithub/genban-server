from dataclasses import dataclass
from typing import Any

from src.agent.entities import Chat


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
    result: ToolExecute

@dataclass
class ToolExecute:
    """工具执行结果"""

    result_content: str
    tool_chats: list[Chat] | None = None
    error: bool = False