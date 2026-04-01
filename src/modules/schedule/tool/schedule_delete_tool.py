"""删除日程工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.modules.schedule.component.schedule_manager import schedule_manager

logger = get_logger(__name__)


class ScheduleDeleteTool(BaseTool):
    """删除日程工具"""

    name = "schedule_delete"
    description = "删除一个日程安排"
    parameters = [
        ToolParameter(
            name="schedule_id",
            type="integer",
            description="要删除的日程ID",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行删除日程操作

        Args:
            context: Agent 执行上下文
            schedule_id: 日程ID

        Returns:
            删除结果消息
        """
        try:
            user_id = context.user_id
            schedule_id = kwargs.get("schedule_id")

            if not schedule_id:
                return "错误：请提供日程ID"

            success = schedule_manager.delete_schedule(user_id, schedule_id)
            if success:
                logger.info(f"删除日程成功，user_id: {user_id}, schedule_id: {schedule_id}")
                return f"日程删除成功！日程ID: {schedule_id}"
            else:
                return f"错误：找不到ID为 {schedule_id} 的日程"

        except Exception as e:
            logger.exception(
                f"删除日程失败，user_id: {context.user_id}, schedule_id: {kwargs.get('schedule_id')}"
            )
            return f"删除日程失败: {str(e)}"
