import secrets

from src.user.exceptions import (
    UserNotFoundException,
    InvalidPasswordException,
    UnauthorizedException,
)
from src.common.utils import time_util
from src.user.db.models import UserState
from src.user.db.user_db import user_db
from src.user.db.user_state_db import user_state_db
from src.user.components.password_util import verifyPassword


class _UserManager:
    # 用户管理器 - 状态管理和认证

    TOKEN_EXPIRE_SECONDS = 7 * time_util.ONE_DAY_SECOND  # 7天

    def getState(self, userid: str) -> UserState:
        # 获取用户状态
        state = user_state_db.get_by_user_id(userid)
        if state is None:
            raise UserNotFoundException(userid)
        return state

    def updateState(self, state: UserState) -> bool:
        # 更新用户状态
        return user_state_db.update(state)

    def login(self, userId: str, password: str) -> UserState:
        # 登录，成功返回用户状态
        user = user_db.get_user_by_id(userId)
        if user is None:
            raise UserNotFoundException(userId)

        if not verifyPassword(password, user.password_hash):
            raise InvalidPasswordException()

        state = user_state_db.get_by_user_id(userId)
        if state is None:
            raise UserNotFoundException(userId)

        # 创建 token
        state.token = secrets.token_urlsafe(32)
        state.token_expires_at = time_util.get_timestamp() + self.TOKEN_EXPIRE_SECONDS

        # 持久化到数据库
        user_state_db.update(state)

        return state

    def validateToken(self, token: str) -> str:
        # 校验 token，返回 user_id
        state = user_state_db.get_by_token(token)
        if state is None:
            raise UnauthorizedException()

        if state.token_expires_at < time_util.get_timestamp():
            # token 过期
            raise UnauthorizedException()

        return state.user_id


user_manager = _UserManager()
