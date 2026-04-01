"""日程数据访问层"""

from typing import List

from src.common.utils.time_util import get_timestamp
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import Schedule


class ScheduleRepository:
    """日程 Repository 类，提供日程的增删改查操作"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @db_execute
    def create(self, db, schedule: Schedule) -> Schedule:
        """创建日程

        Args:
            db: 数据库会话
            schedule: 日程对象

        Returns:
            创建后的日程对象（包含生成的ID）
        """
        now = get_timestamp()
        schedule.created_at = now
        schedule.updated_at = now
        db.add(schedule)
        db.flush()
        return schedule

    @db_query
    def get_by_id(self, db, schedule_id: int, user_id: str) -> Schedule | None:
        """根据ID获取日程（带用户隔离）

        Args:
            db: 数据库会话
            schedule_id: 日程ID
            user_id: 用户ID

        Returns:
            日程对象，不存在则返回 None
        """
        return (
            db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.user_id == user_id)
            .first()
        )

    @db_query
    def list_by_user(self, db, user_id: str, enabled_only: bool = False) -> List[Schedule]:
        """获取用户的所有日程

        Args:
            db: 数据库会话
            user_id: 用户ID
            enabled_only: 是否只返回启用的日程

        Returns:
            日程列表
        """
        query = db.query(Schedule).filter(Schedule.user_id == user_id)
        if enabled_only:
            query = query.filter(Schedule.enabled)
        return query.order_by(Schedule.created_at.desc()).all()

    @db_execute
    def update(self, db, schedule: Schedule) -> Schedule:
        """更新日程

        Args:
            db: 数据库会话
            schedule: 日程对象

        Returns:
            更新后的日程对象
        """
        schedule.updated_at = get_timestamp()
        db.merge(schedule)
        return schedule

    @db_execute
    def delete(self, db, schedule_id: int, user_id: str) -> bool:
        """删除日程（软删除，将 enabled 置为 false）

        Args:
            db: 数据库会话
            schedule_id: 日程ID
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        schedule = (
            db.query(Schedule)
            .filter(Schedule.id == schedule_id, Schedule.user_id == user_id)
            .first()
        )
        if schedule:
            schedule.enabled = False
            schedule.updated_at = get_timestamp()
            db.merge(schedule)
            return True
        return False


# 单例实例
schedule_repository = ScheduleRepository()
