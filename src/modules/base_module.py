"""模块抽象基类定义"""

from abc import ABC, abstractmethod
from typing import ClassVar

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool


class BaseModule(ABC):
    """模块抽象基类，定义模块标准接口

    子类通过类属性定义模块元数据，在__init__中初始化tools和hooks。
    类似 BaseTool 的设计，实现简单直观。
    """

    # 类属性：模块元数据
    id: ClassVar[str] = ""  # 模块唯一标识符
    name: ClassVar[str] = ""  # 模块名称
    description: ClassVar[str] = ""  # 模块描述说明
    message_tag: ClassVar[str | None] = None  # 模块消息标签
    message_tag_instruction: ClassVar[str | None] = None  # 消息标签说明
    relevant_skills: ClassVar[list[str] | None] = None  # 相关技能ID列表

    @abstractmethod
    def get_tools(self) -> list[BaseTool]:
        """返回模块提供的工具列表"""
        pass

    @abstractmethod
    def get_hooks(self) -> list[BaseHook]:
        """返回模块提供的钩子列表"""
        pass

    def to_prompt(self) -> str:
        """生成模块描述用于系统提示词"""
        lines = ["<module>"]
        lines.append(f"<name>{self.name}</name>")
        lines.append(f"<description>{self.description}</description>")
        if self.message_tag:
            lines.append(f"<message_tag>{self.message_tag}</message_tag>")
        if self.message_tag_instruction:
            lines.append(
                f"<message_tag_instruction>{self.message_tag_instruction}</message_tag_instruction>"
            )
        if self.relevant_skills:
            lines.append(f"<relevant_skills>{','.join(self.relevant_skills)}</relevant_skills>")
        # 添加工具信息到提示词
        tools = self.get_tools()
        if tools:
            tool_names = [tool.name for tool in tools]
            lines.append(f"<relevant_tools>{','.join(tool_names)}</relevant_tools>")
        lines.append("</module>")
        return "\n".join(lines)
