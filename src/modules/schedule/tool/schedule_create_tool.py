"""创建日程工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.common.utils.time_util import get_timestamp, timestamp_to_date_time_str
from src.modules.schedule.component.schedule_calculator import schedule_calculator
from src.modules.schedule.component.schedule_manager import schedule_manager

logger = get_logger(__name__)


class ScheduleCreateTool(BaseTool):
    """创建日程工具"""

    name = "schedule_create"
    description = "创建一个新的日程安排"
    parameters = [
        ToolParameter(
            name="title",
            type="string",
            description="日程标题，简要描述日程内容",
            required=True,
        ),
        ToolParameter(
            name="content",
            type="string",
            description="日程详细内容描述",
            required=False,
        ),
        ToolParameter(
            name="cron_expression",
            type="string",
            description="cron 表达式，用于设置日程触发时间。格式：秒 分 时 日 月 周 年（如：'0 0 9 * * 1 *' 表示每周一9点，'0 0 19 1 11 * 2023' 表示2023年11月1日19点）",
            required=True,
        ),
        ToolParameter(
            name="remind_enabled",
            type="boolean",
            description="是否开启主动提醒，默认为 true",
            required=False,
        ),
        ToolParameter(
            name="onetime",
            type="boolean",
            description="是否为一次性日程，触发后自动删除，默认为 false",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行创建日程操作

        Args:
            context: Agent 执行上下文
            title: 日程标题
            content: 日程内容
            cron_expression: cron 表达式
            remind_enabled: 是否开启提醒

        Returns:
            创建结果消息
        """
        try:
            user_id = context.user_id
            title = kwargs.get("title", "")
            content = kwargs.get("content", "")
            cron_expression = kwargs.get("cron_expression", "")
            remind_enabled = kwargs.get("remind_enabled", True)
            onetime = kwargs.get("onetime", False)

            if not title:
                return "错误：请提供日程标题"

            if not cron_expression:
                return "错误：请提供 cron 表达式"

            created = schedule_manager.create_schedule(
                user_id=user_id,
                title=title,
                cron_expression=cron_expression,
                content=content,
                remind_enabled=remind_enabled,
                onetime=onetime,
            )

            # 计算下次触发时间
            next_trigger_times = schedule_calculator.get_next_trigger_times(
                created, get_timestamp(), 1
            )
            next_trigger_str = "未知"
            if next_trigger_times:
                next_trigger_str = timestamp_to_date_time_str(next_trigger_times[0])

            logger.info(f"创建日程成功，user_id: {user_id}, schedule_id: {created.id}")
            return f"日程创建成功！日程ID: {created.id}，标题: {title}，下次触发时间: {next_trigger_str}"

        except Exception as e:
            logger.exception(f"创建日程失败，user_id: {context.user_id}")
            return f"创建日程失败: {str(e)}"
