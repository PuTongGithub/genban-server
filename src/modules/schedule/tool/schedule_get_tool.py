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
            description="要查询的日程ID，不传则返回所有日程",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行获取日程详情操作

        Args:
            context: Agent 执行上下文
            schedule_id: 日程ID，不传则返回所有日程

        Returns:
            日程详情或列表JSON字符串
        """
        try:
            user_id = context.user_id
            schedule_id = kwargs.get("schedule_id")

            # 不传ID时返回所有日程
            if not schedule_id:
                return self._get_all_schedules(user_id)

            # 传入ID时返回单个日程详情
            return self._get_schedule_detail(schedule_id, user_id)

        except Exception as e:
            logger.exception(
                f"获取日程失败，user_id: {context.user_id}, schedule_id: {kwargs.get('schedule_id')}"
            )
            return json.dumps({"error": f"获取日程失败: {str(e)}"}, ensure_ascii=False)

    def _get_all_schedules(self, user_id: str) -> str:
        """获取用户所有日程信息"""
        schedules = schedule_manager.list_schedules(user_id, enabled_only=True)
        now = get_timestamp()
        result_list = [self._build_schedule_info(s, now) for s in schedules]
        return json.dumps(result_list, ensure_ascii=False)

    def _get_schedule_detail(self, schedule_id: int, user_id: str) -> str:
        """获取单个日程详情"""
        schedule = schedule_manager.get_schedule(schedule_id, user_id)
        if not schedule:
            return json.dumps({"error": f"找不到ID为 {schedule_id} 的日程"}, ensure_ascii=False)
        now = get_timestamp()
        result = self._build_schedule_info(schedule, now)
        return json.dumps(result, ensure_ascii=False)

    def _build_schedule_info(self, schedule: Any, now: int) -> dict:
        """构建日程信息字典"""
        next_trigger_times = schedule_calculator.get_next_trigger_times(schedule, now, 3)
        next_trigger_times_str = [timestamp_to_date_time_str(ts) for ts in next_trigger_times]
        return {
            "id": schedule.id,
            "title": schedule.title,
            "content": schedule.content or "",
            "cron_expression": schedule.cron_expression,
            "remind_enabled": schedule.remind_enabled,
            "enabled": schedule.enabled,
            "next_trigger_times": next_trigger_times_str,
        }
