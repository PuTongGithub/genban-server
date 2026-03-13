"""Skills 模块实体类"""

import html
from dataclasses import dataclass
from pathlib import Path
from pydantic import BaseModel


@dataclass
class Skill:
    """Skill 实体"""

    id: str  # Skill ID，文件夹名
    name: str  # Skill 名称，从 YAML 读取
    description: str  # Skill 描述内容
    source_path: Path  # Skill 所在路径

    def to_prompt_line(self):
        """返回 Skill 行信息"""
        id = html.escape(self.id)
        des = html.escape(self.description)
        return f"{id}:{des}"

    def get_skill_md_path(self) -> Path:
        """获取 SKILL.md 文件路径"""
        return self.source_path / "SKILL.md"


class SkillInfo(BaseModel):
    """Skill 信息响应模型"""

    id: str  # Skill ID
    name: str  # Skill 名称
    description: str  # Skill 描述内容


class SkillListResponse(BaseModel):
    """Skill 列表响应模型"""

    skills: list[SkillInfo]  # Skill 列表


class SkillDeleteResponse(BaseModel):
    """Skill 删除响应模型"""

    success: bool  # 是否删除成功
