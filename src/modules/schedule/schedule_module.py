"""日程模块"""

from src.modules.base_module import BaseModule
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook


class ScheduleModule(BaseModule):
    """日程模块"""

    id = "schedule"
    name = "日程模块(目前未实装)"
    description = "提供了对用户日程的管理能力"
    message_tag = "[schedule]"
    message_tag_instruction = "标签后跟日程内容提醒"

    def __init__(self) -> None:
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
