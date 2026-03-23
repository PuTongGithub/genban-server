from typing import Optional

from src.common.utils import time_util
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import User


class _UserDb:
    # 用户数据访问层

    @db_execute
    def create(self, db, user_id: str, password_hash: str) -> bool:
        # 创建用户，返回是否成功
        try:
            user = User(
                user_id=user_id,
                password_hash=password_hash,
                created_at=time_util.get_timestamp(),
            )
            db.add(user)
            return True
        except Exception:
            return False

    @db_query
    def get_user_by_id(self, db, user_id: str) -> Optional[User]:
        # 根据 user_id 查询用户
        return db.query(User).filter(User.user_id == user_id).first()

    @db_execute
    def delete(self, db, user_id: str) -> bool:
        # 删除用户，返回是否成功
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            db.delete(user)
            return True
        return False


user_db = _UserDb()
