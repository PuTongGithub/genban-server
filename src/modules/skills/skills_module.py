"""技能模块"""

from src.modules.base_module import BaseModule
from src.modules.skills.skill_tool import SkillTool
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook


class SkillsModule(BaseModule):
    """技能模块"""

    id = "skills"
    name = "技能模块"
    description = "提供了专业技能和领域知识，可以用于帮助用户完成任务。详细说明请参考下方 system_remainder 中关于技能的详细说明"

    def __init__(self) -> None:
        """初始化技能模块，创建工具实例"""
        self._tools: list[BaseTool] = [SkillTool()]
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
