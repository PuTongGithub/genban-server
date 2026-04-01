"""日程管理器 - 收拢所有日程变更和查询操作"""

from typing import List

from src.common.logger import get_logger
from src.modules.schedule.db.schedule_repository import schedule_repository
from src.modules.schedule.scheduler.scheduler import scheduler
from src.storage.sqlite.models import Schedule

logger = get_logger(__name__)


class ScheduleManager:
    """日程管理器，收拢所有对日程表的变更和查询操作"""

    def create_schedule(
        self,
        user_id: str,
        title: str,
        cron_expression: str,
        content: str | None = None,
        remind_enabled: bool = True,
    ) -> Schedule:
        """创建日程

        Args:
            user_id: 用户ID
            title: 日程标题
            cron_expression: cron表达式
            content: 日程内容
            remind_enabled: 是否开启提醒

        Returns:
            创建的日程对象
        """
        schedule = Schedule(
            user_id=user_id,
            title=title,
            content=content,
            cron_expression=cron_expression,
            remind_enabled=remind_enabled,
            enabled=True,
        )
        created = schedule_repository.create(schedule)

        # 通知调度器添加任务
        scheduler.add_schedule(user_id, created)

        logger.info(f"创建日程成功: user_id={user_id}, schedule_id={created.id}")
        return created

    def update_schedule(
        self,
        user_id: str,
        schedule_id: int,
        title: str | None = None,
        content: str | None = None,
        cron_expression: str | None = None,
        remind_enabled: bool | None = None,
    ) -> Schedule | None:
        """更新日程

        Args:
            user_id: 用户ID
            schedule_id: 日程ID
            title: 新标题
            content: 新内容
            cron_expression: 新cron表达式
            remind_enabled: 是否开启提醒

        Returns:
            更新后的日程对象，不存在则返回None
        """
        schedule = schedule_repository.get_by_id(schedule_id, user_id)
        if not schedule:
            return None

        # 更新字段
        if title is not None:
            schedule.title = title
        if content is not None:
            schedule.content = content
        if cron_expression is not None:
            schedule.cron_expression = cron_expression
        if remind_enabled is not None:
            schedule.remind_enabled = remind_enabled

        updated = schedule_repository.update(schedule)

        # 通知调度器更新任务
        scheduler.update_schedule(user_id, updated)

        logger.info(f"更新日程成功: user_id={user_id}, schedule_id={schedule_id}")
        return updated

    def delete_schedule(self, user_id: str, schedule_id: int) -> bool:
        """删除日程（软删除）

        Args:
            user_id: 用户ID
            schedule_id: 日程ID

        Returns:
            是否删除成功
        """
        success = schedule_repository.delete(schedule_id, user_id)

        if success:
            # 通知调度器移除任务
            scheduler.remove_schedule(user_id, schedule_id)
            logger.info(f"删除日程成功: user_id={user_id}, schedule_id={schedule_id}")

        return success

    def list_schedules(self, user_id: str, enabled_only: bool = False) -> List[Schedule]:
        """查询用户的日程列表

        Args:
            user_id: 用户ID
            enabled_only: 是否只返回启用的日程

        Returns:
            日程列表
        """
        return schedule_repository.list_by_user(user_id, enabled_only)

    def get_schedule(self, schedule_id: int, user_id: str) -> Schedule | None:
        """获取日程详情

        Args:
            schedule_id: 日程ID
            user_id: 用户ID

        Returns:
            日程对象，不存在则返回None
        """
        return schedule_repository.get_by_id(schedule_id, user_id)


# 单例实例
schedule_manager = ScheduleManager()
