"""获取日程详情工具"""

import json
from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.common.utils.time_util import get_timestamp, timestamp_to_date_time_str
from src.modules.schedule.component.schedule_calculator import schedule_calculator
from src.modules.schedule.component.schedule_manager import schedule_manager

logger = get_logger(__name__)


class ScheduleGetTool(BaseTool):
    """获取日程详情工具"""

    name = "schedule_get"
    description = "获取指定日程的详细信息"
    parameters = [
        ToolParameter(
            name="schedule_id",
            type="integer",
            description="要查询的日程ID",
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行获取日程详情操作

        Args:
            context: Agent 执行上下文
            schedule_id: 日程ID

        Returns:
            日程详情JSON字符串
        """
        try:
            user_id = context.user_id
            schedule_id = kwargs.get("schedule_id")

            if not schedule_id:
                return json.dumps({"error": "请提供日程ID"}, ensure_ascii=False)

            schedule = schedule_manager.get_schedule(schedule_id, user_id)
            if not schedule:
                return json.dumps({"error": f"找不到ID为 {schedule_id} 的日程"}, ensure_ascii=False)

            # 获取后3次触发时间
            now = get_timestamp()
            next_trigger_times = schedule_calculator.get_next_trigger_times(schedule, now, 3)
            next_trigger_times_str = [timestamp_to_date_time_str(ts) for ts in next_trigger_times]

            result = {
                "id": schedule.id,
                "title": schedule.title,
                "content": schedule.content or "",
                "cron_expression": schedule.cron_expression,
                "remind_enabled": schedule.remind_enabled,
                "enabled": schedule.enabled,
                "next_trigger_times": next_trigger_times_str,
            }

            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            logger.exception(
                f"获取日程详情失败，user_id: {context.user_id}, schedule_id: {kwargs.get('schedule_id')}"
            )
            return json.dumps({"error": f"获取日程详情失败: {str(e)}"}, ensure_ascii=False)
