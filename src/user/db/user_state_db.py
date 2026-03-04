from typing import Optional
from src.storage.sqlite.database import db_execute, db_query
from src.user.db.models import UserState
from src.common.utils import time_util


class _UserStateDb:
    # 用户状态数据访问层

    @db_execute
    def create(self, db, user_id: str) -> bool:
        # 创建用户状态
        try:
            state = UserState(
                user_id=user_id,
                updated_at=time_util.get_timestamp(),
                token=user_id,
                token_expires_at=0,
            )
            db.add(state)
            return True
        except Exception:
            return False

    @db_execute
    def update(self, db, state: UserState) -> bool:
        # 更新用户状态
        existing = (
            db.query(UserState).filter(UserState.user_id == state.user_id).first()
        )
        if existing:
            existing.updated_at = time_util.get_timestamp()
            existing.token = state.token
            existing.token_expires_at = state.token_expires_at
            return True
        return False

    @db_query
    def get_by_user_id(self, db, user_id: str) -> Optional[UserState]:
        # 根据 user_id 查询用户状态
        return db.query(UserState).filter(UserState.user_id == user_id).first()

    @db_query
    def get_by_token(self, db, token: str) -> Optional[UserState]:
        # 根据 token 查询用户状态
        return db.query(UserState).filter(UserState.token == token).first()

    @db_execute
    def delete(self, db, user_id: str) -> bool:
        # 删除用户状态，返回是否成功
        state = db.query(UserState).filter(UserState.user_id == user_id).first()
        if state:
            db.delete(state)
            return True
        return False


user_state_db = _UserStateDb()
