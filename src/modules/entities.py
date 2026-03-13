from dataclasses import dataclass


@dataclass
class Module:
    """模块实体"""

    name: str
    description: str
    message_tag: str | None = None  # 模块消息标签，用于在系统提示词中标识模块消息
    message_tag_instruction: str | None = None  # 模块消息标签说明
    relevant_skills: list[str] | None = None  # 相关技能 ID 列表
    relevant_tools: list[str] | None = None  # 相关工具 ID 列表
