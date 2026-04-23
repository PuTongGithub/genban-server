"""更新日程工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.modules.schedule.component.schedule_manager import schedule_manager

logger = get_logger(__name__)


class ScheduleUpdateTool(BaseTool):
    """更新日程工具"""

    name = "schedule_update"
    description = "更新一个已有的日程安排，不传的参数将保持不变"
    parameters = [
        ToolParameter(
            name="schedule_id",
            type="integer",
            description="要更新的日程ID",
            required=True,
        ),
        ToolParameter(
            name="title",
            type="string",
            description="新的日程标题",
            required=False,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="新的日程内容",
            required=False,
        ),
        ToolParameter(
            name="cron_expression",
            type="string",
            description="新的 cron 表达式",
            required=False,
        ),
        ToolParameter(
            name="remind_enabled",
            type="boolean",
            description="是否开启提醒",
            required=False,
        ),
        ToolParameter(
            name="onetime",
            type="boolean",
            description="是否为一次性日程，触发后自动删除",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行更新日程操作

        Args:
            context: Agent 执行上下文
            schedule_id: 日程ID
            title: 日程标题
            content: 日程内容
            cron_expression: cron 表达式
            remind_enabled: 是否开启提醒

        Returns:
            更新结果消息
        """
        try:
            user_id = context.user_id
            schedule_id = kwargs.get("schedule_id")

            if not schedule_id:
                return "错误：请提供日程ID"

            # 先查询日程是否存在
            schedule = schedule_manager.get_schedule(schedule_id, user_id)
            if not schedule:
                return f"错误：找不到ID为 {schedule_id} 的日程"

            # 使用 schedule_manager 更新
            updated = schedule_manager.update_schedule(
                user_id=user_id,
                schedule_id=schedule_id,
                title=kwargs.get("title"),
                content=kwargs.get("content"),
                cron_expression=kwargs.get("cron_expression"),
                remind_enabled=kwargs.get("remind_enabled"),
                onetime=kwargs.get("onetime"),
            )

            if updated:
                logger.info(f"更新日程成功，user_id: {user_id}, schedule_id: {schedule_id}")
                return f"日程更新成功！日程ID: {schedule_id}"
            else:
                return "错误：更新日程失败"

        except Exception as e:
            logger.exception(
                f"更新日程失败，user_id: {context.user_id}, schedule_id: {kwargs.get('schedule_id')}"
            )
            return f"更新日程失败: {str(e)}"
