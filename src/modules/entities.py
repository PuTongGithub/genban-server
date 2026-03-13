from dataclasses import dataclass


@dataclass
class Module:
    """模块实体"""

    id: str  # 模块唯一标识符
    name: str  # 模块名称
    description: str  # 模块描述说明
    message_tag: str | None = None  # 模块消息标签，用于在系统提示词中标识模块消息
    message_tag_instruction: str | None = None  # 模块消息标签说明
    relevant_skills: list[str] | None = None  # 相关技能 ID 列表
    relevant_tools: list[str] | None = None  # 相关工具 ID 列表

    def to_xml_str(self) -> str:
        """将模块实体转换为 XML 字符串"""
        lines = ["<module>"]
        lines.append(f"<name>{self.name}</name>")
        lines.append(f"<description>{self.description}</description>")
        if self.message_tag:
            lines.append(f"<message_tag>{self.message_tag}</message_tag>")
        if self.message_tag_instruction:
            lines.append(f"<message_tag_instruction>{self.message_tag_instruction}</message_tag_instruction>")
        if self.relevant_skills:
            lines.append(f"<relevant_skills>{','.join(self.relevant_skills)}</relevant_skills>")
        if self.relevant_tools:
            lines.append(f"<relevant_tools>{','.join(self.relevant_tools)}</relevant_tools>")
        lines.append("</module>")
        return "\n".join(lines)
