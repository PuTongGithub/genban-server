import secrets

from src.user.exceptions import (
    UserNotFoundException,
    InvalidPasswordException,
    UnauthorizedException,
)
from src.common.utils import time_util
from src.common.utils.rsa_util import RsaUtil
from src.config.config import file_config
from src.user.db.models import UserState
from src.user.db.user_db import user_db
from src.user.db.user_state_db import user_state_db
from src.user.components.password_util import (
    verify_password,
    hash_password,
    validate_password,
)


class _UserManager:
    # 用户管理器 - 状态管理和认证

    TOKEN_EXPIRE_SECONDS = 7 * time_util.ONE_DAY_SECOND  # 7天

    def __init__(self):
        # 初始化RSA工具，从文件加载私钥用于解密
        private_key = file_config.get_private_key()
        self._rsa = RsaUtil(private_key_content=private_key) if private_key else None

    def login_or_register(self, userId: str, encrypted_password: str) -> UserState:
        # 登录或自动注册，成功返回用户状态，encrypted_password为RSA加密后的密文
        password = self._rsa.decrypt(encrypted_password)
        user = user_db.get_user_by_id(userId)

        if user is None:
            # 用户不存在，自动注册
            return self._do_register(userId, password)
        else:
            # 用户存在，执行登录验证
            return self._do_login(user, password)

    def validate_token(self, token: str) -> str:
        # 校验token，返回user_id
        state = user_state_db.get_by_token(token)
        if state is None:
            raise UnauthorizedException()

        if state.token_expires_at < time_util.get_timestamp():
            # token过期
            raise UnauthorizedException()

        return state.user_id

    def _do_register(self, userId: str, password: str) -> UserState:
        # 注册新用户
        validate_password(password)

        password_hash = hash_password(password)
        if not user_db.create(userId, password_hash):
            raise RuntimeError("用户创建失败")

        if not user_state_db.create(userId):
            raise RuntimeError("用户状态初始化失败")

        return self._create_token(userId)

    def _do_login(self, user, password: str) -> UserState:
        # 登录验证
        if not verify_password(password, user.password_hash):
            raise InvalidPasswordException()

        return self._create_token(user.user_id)

    def _create_token(self, user_id: str) -> UserState:
        # 创建token并设置过期时间，返回用户状态
        state = user_state_db.get_by_user_id(user_id)
        if state is None:
            raise UserNotFoundException(user_id)

        state.token = secrets.token_urlsafe(32)
        state.token_expires_at = time_util.get_timestamp() + self.TOKEN_EXPIRE_SECONDS

        user_state_db.update(state)
        return state


user_manager = _UserManager()
