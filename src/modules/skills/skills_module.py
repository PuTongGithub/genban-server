"""技能模块"""

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool
from src.modules.base_module import BaseModule
from src.modules.skills.skill_prompt_hook import SkillPromptHook
from src.modules.skills.skill_tool import SkillTool


class SkillsModule(BaseModule):
    """技能模块"""

    id = "skills"
    name = "技能模块"
    description = "提供了专业技能和领域知识。详细说明请参考对话中 skill_prompt_prompt 部分的内容"

    def __init__(self) -> None:
        """初始化技能模块，创建工具实例"""
        self._tools: list[BaseTool] = [SkillTool()]
        self._hooks: list[BaseHook] = [SkillPromptHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
