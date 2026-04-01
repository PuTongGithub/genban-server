"""日程计算组件"""

from dataclasses import dataclass
from datetime import datetime, timezone

from apscheduler.triggers.cron import CronTrigger

from src.common.logger import get_logger
from src.storage.sqlite.models import Schedule

logger = get_logger(__name__)


@dataclass
class ScheduleWithNextTime:
    """带下次触发时间的日程信息"""

    schedule: Schedule
    next_trigger_time: int | None = None


class ScheduleCalculator:
    """日程计算组件，提供日程触发时间计算能力"""

    def _parse_cron_expression(self, cron_expression: str) -> dict[str, str]:
        """解析cron表达式为APScheduler CronTrigger参数

        Args:
            cron_expression: cron表达式（秒 分 时 日 月 周 年）

        Returns:
            CronTrigger参数字典
        """
        parts = cron_expression.split()

        # 支持7字段格式（秒 分 时 日 月 周 年）或6字段格式（秒 分 时 日 月 周）
        if len(parts) == 7:
            return {
                "second": parts[0],
                "minute": parts[1],
                "hour": parts[2],
                "day": parts[3],
                "month": parts[4],
                "day_of_week": parts[5],
                "year": parts[6],
            }
        elif len(parts) == 6:
            return {
                "second": parts[0],
                "minute": parts[1],
                "hour": parts[2],
                "day": parts[3],
                "month": parts[4],
                "day_of_week": parts[5],
            }
        else:
            # 尝试标准5字段格式（分 时 日 月 周），秒默认为0
            if len(parts) == 5:
                return {
                    "second": "0",
                    "minute": parts[0],
                    "hour": parts[1],
                    "day": parts[2],
                    "month": parts[3],
                    "day_of_week": parts[4],
                }
            raise ValueError(f"不支持的cron表达式格式: {cron_expression}")

    def get_trigger_times_in_range(
        self,
        schedules: list[Schedule],
        start_timestamp: int,
        end_timestamp: int,
    ) -> tuple[dict[int, ScheduleWithNextTime], list[tuple[int, int]]]:
        """获取指定时间范围内所有日程的触发时间列表

        Args:
            schedules: 日程列表
            start_timestamp: 起始时间戳
            end_timestamp: 结束时间戳

        Returns:
            tuple: (id到ScheduleWithNextTime的映射, 按时间排序的(触发时间戳, 日程id)列表)
        """
        # 收集所有触发事件
        trigger_events: list[tuple[int, int]] = []

        start_dt = datetime.fromtimestamp(start_timestamp, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(end_timestamp, tz=timezone.utc)

        # 记录每个日程的下次触发时间
        next_trigger_map: dict[int, int | None] = {}

        for schedule in schedules:
            try:
                cron_params = self._parse_cron_expression(schedule.cron_expression)
                trigger = CronTrigger(**cron_params)

                # 获取第一个触发时间（用于记录下次触发时间）
                first_fire_time = trigger.get_next_fire_time(None, start_dt)
                if first_fire_time:
                    next_trigger_map[schedule.id] = int(first_fire_time.timestamp())

                    # 收集时间范围内的所有触发时间
                    current_fire_time = first_fire_time
                    while current_fire_time and current_fire_time <= end_dt:
                        fire_timestamp = int(current_fire_time.timestamp())
                        trigger_events.append((fire_timestamp, schedule.id))
                        current_fire_time = trigger.get_next_fire_time(
                            current_fire_time, current_fire_time
                        )

            except Exception:
                logger.exception(
                    f"日程 {schedule.id} 的 cron 表达式 {schedule.cron_expression} 解析失败"
                )
                next_trigger_map[schedule.id] = None
                continue

        # 按时间排序
        trigger_events.sort(key=lambda x: x[0])

        # 构建包含下次触发时间的映射
        schedule_map: dict[int, ScheduleWithNextTime] = {}
        for schedule in schedules:
            schedule_map[schedule.id] = ScheduleWithNextTime(
                schedule=schedule,
                next_trigger_time=next_trigger_map.get(schedule.id),
            )

        return schedule_map, trigger_events

    def get_next_trigger_times(
        self,
        schedule: Schedule,
        from_timestamp: int,
        count: int,
    ) -> list[int]:
        """获取日程在指定时间后的N次触发时间列表

        Args:
            schedule: 日程对象
            from_timestamp: 起始时间戳（从此时间之后开始计算）
            count: 需要获取的触发次数

        Returns:
            触发时间戳列表（按时间顺序）
        """
        if count <= 0:
            return []

        trigger_times: list[int] = []

        try:
            from_dt = datetime.fromtimestamp(from_timestamp, tz=timezone.utc)
            cron_params = self._parse_cron_expression(schedule.cron_expression)
            trigger = CronTrigger(**cron_params)

            # 获取第一次触发时间
            current_fire_time = trigger.get_next_fire_time(None, from_dt)

            # 收集count次触发时间
            collected = 0
            while current_fire_time and collected < count:
                trigger_times.append(int(current_fire_time.timestamp()))
                collected += 1
                current_fire_time = trigger.get_next_fire_time(current_fire_time, current_fire_time)

        except Exception:
            logger.exception(
                f"日程 {schedule.id} 的 cron 表达式 {schedule.cron_expression} 解析失败"
            )
            return trigger_times

        return trigger_times


# 单例实例
schedule_calculator = ScheduleCalculator()
