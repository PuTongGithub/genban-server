"""Skill 信息获取工具"""

from typing import Any

from src.agent.entities import AgentContext, ToolParameter
from src.agent.tools.base_tool import BaseTool
from src.modules.skills.skills_manager import skills_manager


class SkillTool(BaseTool):
    """获取 Skill 信息的工具，供模型调用后获取指定 Skill 的目录路径和 SKILL.md 内容"""

    name = "get_skill_info"
    description = "获取指定 Skill 的目录路径和 SKILL.md 内容"
    parameters = [
        ToolParameter(
            name="skill_id",
            type="string",
            description="Skill ID",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行获取 Skill 信息

        Args:
            context: Agent 执行上下文
            skill_id: Skill ID（文件夹名）

        Returns:
            Skill 的目录路径和 SKILL.md 内容
        """
        skill_id = kwargs.get("skill_id", "")

        if not skill_id:
            return "错误：请提供 skill_id 参数"

        # 使用 skills_manager 单例获取 Skill
        skill = skills_manager.get_skill(context.user_id, skill_id)

        if not skill:
            return f"错误：找不到 Skill '{skill_id}'"

        # 读取 SKILL.md 内容
        skill_md_content = skills_manager.read_skill_md_content(skill)
        if skill_md_content is None:
            skill_md_content = "（SKILL.md 内容读取失败）"

        # 构建返回结果
        result = f"""Skill 信息:
- Skill ID: {skill.id}
- 目录路径: {skill.source_path}

SKILL.md 内容:
```markdown
{skill_md_content}
```
"""

        return result
