"""日程提示词 Hook 实现"""

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import PromptHook
from src.common.utils.time_util import (
    ONE_DAY_SECOND,
    get_timestamp,
    get_today_start_timestamp,
    timestamp_to_date_time_str,
)
from src.config.prompts_loader import prompts_loader
from src.modules.schedule.component.schedule_calculator import (
    ScheduleWithNextTime,
    schedule_calculator,
)
from src.modules.schedule.db.schedule_repository import schedule_repository


class SchedulePromptHook(PromptHook):
    """注入日程信息到提示词的钩子"""

    order = 2

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """注入日程信息到上下文

        注入内容：
        1. 当天已过期的日程
        2. 接下来即将触发的日程
        3. 所有 enable=true 的日程基本信息
        """
        user_id = context.user_id

        # 获取所有启用的日程
        all_schedules = schedule_repository.list_by_user(user_id, enabled_only=True)

        # 构建日程信息提示词
        schedule_prompt = self._build_schedule_prompt(all_schedules)

        if schedule_prompt:
            data.append(chat_factory.create_schedule_prompt_chat(schedule_prompt))

        return data

    def _format_schedule_info(self, schedule_with_next_time: ScheduleWithNextTime) -> str:
        """格式化日程基本信息"""
        schedule = schedule_with_next_time.schedule
        content = f"- ID:{schedule.id} | {schedule.title} | cron:{schedule.cron_expression}"
        if schedule_with_next_time.next_trigger_time:
            next_time_str = timestamp_to_date_time_str(schedule_with_next_time.next_trigger_time)
            content += f" | 下次触发: {next_time_str}"
        return content

    def _format_schedule_time(self, schedule_with_next_time: ScheduleWithNextTime, ts: int) -> str:
        """格式化日程触发时间"""
        schedule = schedule_with_next_time.schedule
        time_str = timestamp_to_date_time_str(ts)
        return f"- ID:{schedule.id} | {schedule.title} | 触发时间： {time_str}"

    def _build_schedule_prompt(self, schedules: list) -> str:
        """构建日程信息提示词

        Args:
            schedules: 日程列表

        Returns:
            格式化后的日程提示词
        """
        if not schedules:
            return prompts_loader.get_schedule_prompt(schedule_list="无")

        now = get_timestamp()
        today_start = get_today_start_timestamp()
        future_end = now + ONE_DAY_SECOND

        # 使用schedule_calculator获取时间范围内的触发事件
        schedule_map, trigger_events = schedule_calculator.get_trigger_times_in_range(
            schedules, today_start, future_end
        )

        # 1. 构建所有日程列表
        schedule_list_lines = []
        for schedule in schedules:
            schedule_with_time = schedule_map.get(schedule.id)
            if schedule_with_time and schedule_with_time.next_trigger_time is not None:
                schedule_list_lines.append(self._format_schedule_info(schedule_with_time))
        schedule_list = "\n".join(schedule_list_lines) if schedule_list_lines else "无"

        # 2. 今日已过期的日程（按时间排序取最新5个）
        expired_events = [(ts, sid) for ts, sid in trigger_events if ts < now]
        expired_lines = []
        for ts, sid in expired_events[-5:]:
            schedule_with_time = schedule_map.get(sid)
            if schedule_with_time:
                expired_lines.append(self._format_schedule_time(schedule_with_time, ts))
        expired_schedules_str = "\n".join(expired_lines) if expired_lines else None

        # 3. 接下来的日程(按时间排序取前5个)
        future_events = [(ts, sid) for ts, sid in trigger_events if ts >= now]
        future_lines = []
        for ts, sid in future_events[:5]:
            schedule_with_time = schedule_map.get(sid)
            if schedule_with_time:
                future_lines.append(self._format_schedule_time(schedule_with_time, ts))
        future_schedules_str = "\n".join(future_lines) if future_lines else None

        # 使用 prompts_loader 构建最终提示词
        return prompts_loader.get_schedule_prompt(
            schedule_list=schedule_list,
            expired_schedules=expired_schedules_str,
            future_schedules=future_schedules_str,
        )
