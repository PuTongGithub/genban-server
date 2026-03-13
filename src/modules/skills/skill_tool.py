"""Skill 信息获取工具"""

from typing import Any

from src.agent.entities import AgentContext, ToolParameter
from src.agent.tools.base_tool import BaseTool
from src.modules.skills.skills_manager import skills_manager


class SkillTool(BaseTool):
    """获取 Skill 信息的工具，供模型调用后获取指定 Skill 的目录路径和 SKILL.md 内容"""

    name = "get_skill_info"
    description = """获取指定 Skill 的目录路径和 SKILL.md 内容。
重要提示：
- 当用户要求你执行任务时，检查是否有任何可用技能匹配。技能提供了专业能力和领域知识
- 可用技能列在对话开头 system_remainder 的 available_skills 之中
- 当技能匹配用户请求时，这是阻塞性要求：在生成关于该任务的任何其他响应之前，先调用该工具获得技能信息
- 切勿在不实际调用此工具的情况下提及技能
- 不要调用已在运行中的技能
- 如果你在当前对话中看到 <SKILL:${skill_id}> 标签，表示该技能已加载 - 直接遵循指令，无需再次调用此工具
- 当你需要执行技能中包含的脚本时，请参照get_skill_info工具返回的技能所在目录路径，用绝对路径来执行。例如：Skill 目录路径: /home/user/skills/skill1，脚本路径: /home/user/skills/skill1/scripts/script.sh
"""
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
        result = f"""<SKILL:{skill.id}>
- Skill 目录路径: {skill.source_path}
- Skill.md 文件路径: {skill.get_skill_md_path()}
- SKILL.md 内容:
```markdown
{skill_md_content}
```
</SKILL:{skill.id}>"""

        return result
