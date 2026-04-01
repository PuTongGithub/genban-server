"""日程模块"""

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool
from src.modules.base_module import BaseModule
from src.modules.schedule.hook.schedule_prompt_hook import SchedulePromptHook
from src.modules.schedule.tool.schedule_create_tool import ScheduleCreateTool
from src.modules.schedule.tool.schedule_delete_tool import ScheduleDeleteTool
from src.modules.schedule.tool.schedule_get_tool import ScheduleGetTool
from src.modules.schedule.tool.schedule_update_tool import ScheduleUpdateTool


class ScheduleModule(BaseModule):
    """日程模块"""

    id = "schedule"
    name = "日程模块"
    description = "提供了对用户日程的管理能力，你可以通过工具来添加、删除、查询用户日程，用户也能够在客户端页面查看和管理自己的日程"
    message_tag = "[schedule], [schedule_remainder]"
    message_tag_instruction = "[schedule] 标签后跟当前启用的所有日程信息；当某一条日程的提醒时间到时，你会收到一条带 [schedule_remainder] 标签的日程提醒消息，你可以根据消息内容来做相应的处理"

    def __init__(self) -> None:
        self._tools: list[BaseTool] = [
            ScheduleGetTool(),
            ScheduleCreateTool(),
            ScheduleDeleteTool(),
            ScheduleUpdateTool(),
        ]
        self._hooks: list[BaseHook] = [SchedulePromptHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
