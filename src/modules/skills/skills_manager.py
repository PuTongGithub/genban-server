"""Skills 管理器"""

import html
import shutil

from src.common.utils.path_util import get_user_skills_dir, get_project_skills_dir
from src.modules.skills.entities import Skill
from src.modules.skills.exceptions import SkillNotFoundException
from src.modules.skills.skill_loader import skill_loader


class SkillsManager:
    """Skills 管理器，提供 Skills 的查询和管理功能（单例模式）"""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if SkillsManager._initialized:
            return
        self._skill_loader = skill_loader
        SkillsManager._initialized = True

    def get_user_skills(self, user_id: str) -> list[Skill]:
        """获取用户 Skills

        Args:
            user_id: 用户 ID

        Returns:
            用户 Skills 列表
        """
        user_skills_dir = get_user_skills_dir(user_id)
        return self._skill_loader.load_from_directory(user_skills_dir)

    def delete_user_skill(self, user_id: str, skill_id: str) -> bool:
        """删除用户 Skill

        Args:
            user_id: 用户 ID
            skill_id: Skill ID（文件夹名）

        Returns:
            删除成功返回 True，失败返回 False

        Raises:
            SkillNotFoundException: Skill 不存在
        """
        user_skills_dir = get_user_skills_dir(user_id)
        skill_path = user_skills_dir / skill_id

        if not skill_path.exists():
            raise SkillNotFoundException(f"Skill 不存在: {skill_id}")

        try:
            shutil.rmtree(skill_path)
            return True
        except Exception:
            return False

    def load_all_skills(self, user_id: str) -> list[Skill]:
        """加载用户的所有 Skills

        Args:
            user_id: 用户 ID

        Returns:
            用户 Skills 列表
        """
        return self.get_user_skills(user_id)

    def get_skill(self, user_id: str, skill_id: str) -> Skill | None:
        """获取指定 Skill

        Args:
            user_id: 用户 ID
            skill_id: Skill ID（文件夹名）

        Returns:
            Skill 实体，不存在返回 None
        """
        user_skills_dir = get_user_skills_dir(user_id)
        skill_path = user_skills_dir / skill_id
        if skill_path.exists():
            return self._skill_loader.load_skill(skill_path)

        return None

    def init_user_skills(self, user_id: str) -> bool:
        """初始化用户 Skills，从项目根目录复制默认 Skills

        Args:
            user_id: 用户 ID

        Returns:
            复制成功返回 True，失败返回 False（不影响业务流程）
        """
        project_skills_dir = get_project_skills_dir()
        user_skills_dir = get_user_skills_dir(user_id)

        if not project_skills_dir.exists():
            return False

        try:
            # 复制项目 skills 目录下的所有内容到用户 skills 目录
            for item in project_skills_dir.iterdir():
                if item.is_dir():
                    dest_path = user_skills_dir / item.name
                    if dest_path.exists():
                        shutil.rmtree(dest_path)
                    shutil.copytree(item, dest_path)
            return True
        except Exception:
            return False

    def get_skill_md_content(self, user_id: str, skill_id: str) -> str | None:
        """获取指定 Skill 的 SKILL.md 文件内容

        Args:
            user_id: 用户 ID
            skill_id: Skill ID

        Returns:
            SKILL.md 文件内容，Skill 不存在或文件不存在返回 None
        """
        skill = self.get_skill(user_id, skill_id)

        if skill is None:
            return None

        return self.read_skill_md_content(skill)

    def read_skill_md_content(self, skill: Skill) -> str | None:
        """读取 Skill 的 SKILL.md 文件内容

        Args:
            skill: Skill 实体

        Returns:
            SKILL.md 文件内容，文件不存在或读取失败返回 None
        """
        skill_md_path = skill.source_path / "SKILL.md"

        if not skill_md_path.exists():
            return None

        try:
            return skill_md_path.read_text(encoding="utf-8")
        except Exception:
            return None

    def to_prompt(self, user_id: str) -> str:
        """生成 <available_skills> XML 块，用于包含在 Agent 提示词中

        此 XML 格式是 Anthropic 推荐用于 Claude 模型的格式。

        Args:
            user_id: 用户 ID

        Returns:
            XML 字符串，包含 <available_skills> 块，每个 skill 包含
            name 和 description。

        Example output:
            <available_skills>
            <skill>
            <name>pdf-reader</name>
            <description>Read and extract text from PDF files</description>
            </skill>
            </available_skills>
        """
        skills = self.load_all_skills(user_id)

        if not skills:
            return "<available_skills></available_skills>"

        lines = ["<available_skills>"]

        for skill in skills:
            lines.append("<skill>")
            lines.append("<id>" + html.escape(skill.id) + "</id>")
            lines.append("<name>" + html.escape(skill.name) + "</name>")
            lines.append(
                "<description>" + html.escape(skill.description) + "</description>"
            )
            lines.append("</skill>")

        lines.append("</available_skills>")

        return "\n".join(lines)


# 全局 SkillsManager 单例实例
skills_manager = SkillsManager()
