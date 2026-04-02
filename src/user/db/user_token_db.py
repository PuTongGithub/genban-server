"""用户Token数据访问层"""

from typing import Optional

from src.common.utils import time_util
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import UserToken


class _UserTokenDb:
    # 用户Token数据访问层 - 支持多端同时在线

    @db_execute
    def create_token(self, db, user_id: str, token: str, expires_at: int) -> bool:
        # 创建新token
        try:
            user_token = UserToken(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                created_at=time_util.get_timestamp(),
            )
            db.add(user_token)
            return True
        except Exception:
            return False

    @db_query
    def get_by_token(self, db, token: str) -> Optional[UserToken]:
        # 根据token查询
        return db.query(UserToken).filter(UserToken.token == token).first()

    @db_query
    def get_tokens_by_user_id(self, db, user_id: str) -> list[UserToken]:
        # 根据user_id查询所有token，按创建时间升序排列（最老的在前）
        return (
            db.query(UserToken)
            .filter(UserToken.user_id == user_id)
            .order_by(UserToken.created_at.asc())
            .all()
        )

    @db_execute
    def delete_oldest_token(self, db, user_id: str) -> bool:
        # 删除最老的token
        oldest = (
            db.query(UserToken)
            .filter(UserToken.user_id == user_id)
            .order_by(UserToken.created_at.asc())
            .first()
        )
        if oldest:
            db.delete(oldest)
            return True
        return False

    @db_execute
    def refresh_token(self, db, token: str, new_expires_at: int) -> bool:
        # 刷新token过期时间
        user_token = db.query(UserToken).filter(UserToken.token == token).first()
        if user_token:
            user_token.expires_at = new_expires_at
            return True
        return False

    @db_execute
    def delete_expired_tokens(self, db, user_id: str) -> int:
        # 删除用户的过期token，返回删除数量
        current_time = time_util.get_timestamp()
        expired_tokens = (
            db.query(UserToken)
            .filter(
                UserToken.user_id == user_id,
                UserToken.expires_at < current_time,
            )
            .all()
        )
        count = len(expired_tokens)
        for token in expired_tokens:
            db.delete(token)
        return count

    @db_execute
    def delete_all_tokens(self, db, user_id: str) -> int:
        # 删除用户的所有token，返回删除数量
        tokens = db.query(UserToken).filter(UserToken.user_id == user_id).all()
        count = len(tokens)
        for token in tokens:
            db.delete(token)
        return count


user_token_db = _UserTokenDb()
