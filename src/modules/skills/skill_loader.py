"""Skill 加载器"""

import re
from pathlib import Path
from typing import Any

from src.modules.skills.entities import Skill
from src.modules.skills.exceptions import SkillParseException


class SkillLoader:
    """Skill 加载器，负责从文件系统加载 Skills（单例模式）"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if SkillLoader._initialized:
            return
        SkillLoader._initialized = True

    def load_from_directory(self, directory: Path) -> list[Skill]:
        """从目录加载所有 Skills

        Args:
            directory: Skills 目录路径

        Returns:
            Skill 实体列表
        """
        skills: list[Skill] = []

        if not directory.exists():
            return skills

        for skill_path in directory.iterdir():
            if skill_path.is_dir():
                skill = self.load_skill(skill_path)
                if skill:
                    skills.append(skill)

        return skills

    def load_skill(self, skill_path: Path) -> Skill | None:
        """加载单个 Skill

        Args:
            skill_path: Skill 目录路径

        Returns:
            Skill 实体，加载失败返回 None

        Raises:
            SkillParseException: 解析 SKILL.md 失败
        """
        skill_md_path = skill_path / "SKILL.md"

        if not skill_md_path.exists():
            return None

        try:
            content = skill_md_path.read_text(encoding="utf-8")
            parsed = self._parse_skill_md(content)

            # Skill ID 为文件夹名
            skill_id = skill_path.name
            # Skill 名称从 YAML 中读取，如果没有则使用目录名
            skill_name = parsed.get("name") or skill_path.name

            return Skill(
                id=skill_id,
                name=skill_name,
                description=parsed.get("description", ""),
                source_path=skill_path,
            )
        except Exception as e:
            raise SkillParseException(f"解析 Skill 失败: {skill_path.name}, 错误: {e}")

    def _parse_skill_md(self, content: str) -> dict:
        """解析 SKILL.md 内容，提取 name 和 description

        Args:
            content: SKILL.md 文件内容

        Returns:
            解析后的字典，包含 name 和 description
        """
        result: dict[str, Any] = {
            "name": "",
            "description": "",
        }

        # 解析 YAML frontmatter
        frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            frontmatter = match.group(1)

            # 解析 frontmatter 中的字段
            for line in frontmatter.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")

                    if key == "name":
                        result["name"] = value
                    elif key == "description":
                        result["description"] = value
        else:
            # 没有 frontmatter，取前100字符作为描述
            result["description"] = content.strip()[:100]

        return result


# 全局 SkillLoader 单例实例
skill_loader = SkillLoader()
