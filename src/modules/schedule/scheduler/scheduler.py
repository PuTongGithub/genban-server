"""日程调度器 - 基于 APScheduler 实现"""

from apscheduler.schedulers import SchedulerNotRunningError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.common.logger import get_logger
from src.common.utils.time_util import (
    get_timestamp,
    timestamp_to_date_time_str,
)
from src.modules.schedule.component.schedule_calculator import schedule_calculator
from src.modules.schedule.db.schedule_repository import schedule_repository
from src.storage.sqlite.models import Schedule

logger = get_logger(__name__)


class Scheduler:
    """日程调度器，统一管理所有用户的日程提醒任务"""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler()
        self._scheduler.start()
        logger.info("日程调度器已启动")

    def user_online(self, user_id: str) -> None:
        """用户上线，加载该用户的所有日程到调度器

        Args:
            user_id: 用户ID
        """
        try:
            schedules = schedule_repository.list_by_user(user_id, enabled_only=True)
            for schedule in schedules:
                self.add_schedule(user_id, schedule)
            logger.info(f"用户 {user_id} 上线，已加载 {len(schedules)} 个日程任务")
        except Exception:
            logger.exception(f"加载用户 {user_id} 的日程任务失败")

    def remove_schedule(self, user_id: str, schedule_id: int) -> None:
        """从调度器移除单个日程任务

        Args:
            user_id: 用户ID
            schedule_id: 日程ID
        """
        job_id = self._get_job_id(user_id, schedule_id)
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"已移除日程任务: {schedule_id}")
        except Exception:
            # 任务可能不存在，忽略错误
            pass

    def update_schedule(self, user_id: str, schedule: Schedule) -> None:
        """更新日程任务（先移除再添加）

        Args:
            user_id: 用户ID
            schedule: 日程对象
        """
        self.remove_schedule(user_id, schedule.id)
        if schedule.enabled:
            self.add_schedule(user_id, schedule)
            logger.info(f"已更新日程任务: {schedule.id} - {schedule.title}")

    def add_schedule(self, user_id: str, schedule: Schedule) -> bool:
        """添加日程任务到调度器

        Args:
            user_id: 用户ID
            schedule: 日程对象
        """
        if not schedule.enabled or not schedule.remind_enabled:
            return False

        job_id = self._get_job_id(user_id, schedule.id)

        try:
            # 解析 cron 表达式 (秒 分 时 日 月 周 年)
            cron_parts = schedule.cron_expression.split()
            if len(cron_parts) < 6:
                logger.warning(
                    f"日程 {schedule.id} 的 cron 表达式格式不正确: {schedule.cron_expression}"
                )
                return False

            # 构建 CronTrigger
            trigger = CronTrigger(
                second=cron_parts[0],
                minute=cron_parts[1],
                hour=cron_parts[2],
                day=cron_parts[3],
                month=cron_parts[4],
                day_of_week=cron_parts[5],
                year=cron_parts[6] if len(cron_parts) > 6 else None,
            )

            self._scheduler.add_job(
                func=self._on_schedule_trigger,
                trigger=trigger,
                id=job_id,
                args=[user_id, schedule],
                replace_existing=True,
            )

            logger.info(f"已添加日程任务: {schedule.id} - {schedule.title}")
            return True
        except Exception:
            logger.exception(f"添加日程任务失败: {schedule.id} - {schedule.cron_expression}")
            return False

    def _on_schedule_trigger(self, user_id: str, schedule: Schedule) -> None:
        """日程触发回调

        Args:
            user_id: 用户ID
            schedule: 日程对象
        """
        try:
            from src.agent.chat_factory import chat_factory
            from src.agent.entities import Chat
            from src.assistant.assistant_manager import assistant_manager

            # 构建提醒消息
            now = get_timestamp()
            current_time = timestamp_to_date_time_str(now)
            remind_content = f"""
- 当前时间：{current_time}
- ID:{schedule.id} | {schedule.title}
"""

            if schedule.content:
                remind_content += f"- 内容: {schedule.content}"

            next_trigger_times = schedule_calculator.get_next_trigger_times(schedule, now + 1, 1)
            if next_trigger_times:
                next_trigger_time = timestamp_to_date_time_str(next_trigger_times[0])
            else:
                next_trigger_time = "无"
            remind_content += f"\n- 下次触发时间：{next_trigger_time}"

            chat: Chat = chat_factory.create_schedule_remainder_chat(remind_content)
            assistant_manager.submit_chat(user_id, chat)

            logger.info(f"日程提醒已发送: user_id={user_id}, schedule_id={schedule.id}")
        except Exception:
            logger.exception(f"发送日程提醒失败: user_id={user_id}, schedule_id={schedule.id}")

    def _get_job_id(self, user_id: str, schedule_id: int) -> str:
        """生成任务ID

        Args:
            user_id: 用户ID
            schedule_id: 日程ID

        Returns:
            任务ID
        """
        return f"s_{user_id}_{schedule_id}"

    def shutdown(self) -> None:
        """关闭调度器"""
        try:
            self._scheduler.shutdown()
            logger.info("日程调度器已关闭")
        except SchedulerNotRunningError:
            logger.debug("日程调度器未运行，无需关闭")
        except Exception:
            logger.exception("关闭日程调度器异常")


# 单例实例
scheduler = Scheduler()
