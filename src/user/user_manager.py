"""用户管理模块"""

import secrets

from src.agent.chat_factory import chat_factory
from src.common.utils import time_util
from src.common.utils.rsa_util import RsaUtil
from src.config.config import app_config, file_config
from src.modules.skills.skills_manager import skills_manager
from src.storage.sqlite.models import UserToken
from src.user.components.user_validate_util import (
    hash_password,
    validate_password,
    validate_username,
    verify_password,
)
from src.user.db.user_db import user_db
from src.user.db.user_token_db import user_token_db
from src.user.exceptions import (
    InvalidPasswordException,
    UnauthorizedException,
    UserNotAllowedException,
)
from src.user.user_config_manager import user_config_manager


class _UserManager:
    # 用户管理器 - 状态管理和认证

    TOKEN_EXPIRE_SECONDS = 2 * time_util.ONE_DAY_SECOND  # 48小时
    MAX_TOKENS_PER_USER = 3  # 每个用户最多3个token

    def __init__(self):
        # 初始化RSA工具，从文件加载私钥用于解密
        private_key = file_config.get_private_key()
        self._rsa = RsaUtil(private_key_content=private_key) if private_key else None

    def _is_invite_code_valid(self, invite_code: str) -> bool:
        # 检查邀请码是否在白名单中
        invite_codes = app_config.get("auth").get("invite_codes", [])
        # 如果邀请码列表为空，允许所有注册
        if not invite_codes:
            return True
        return invite_code in invite_codes

    def login_or_register(
        self, user_id: str, encrypted_password: str, invite_code: str = ""
    ) -> UserToken:
        # 登录或自动注册，成功返回用户token信息，encrypted_password为RSA加密后的密文
        password = self._rsa.decrypt(encrypted_password)
        user = user_db.get_user_by_id(user_id)

        if user is None:
            # 用户不存在，自动注册，需要校验邀请码
            if not self._is_invite_code_valid(invite_code):
                raise UserNotAllowedException()
            return self._do_register(user_id, password)
        else:
            # 用户存在，执行登录验证，不校验邀请码
            return self._do_login(user, password)

    def validate_token(self, token: str) -> str:
        # 校验token，返回user_id
        user_token = user_token_db.get_by_token(token)
        if user_token is None:
            raise UnauthorizedException()

        if user_token.expires_at < time_util.get_timestamp():
            # token过期
            raise UnauthorizedException()

        return user_token.user_id

    def refresh_token(self, token: str) -> bool:
        # 刷新token过期时间，返回是否成功
        user_token = user_token_db.get_by_token(token)
        if user_token is None:
            return False

        new_expires_at = time_util.get_timestamp() + self.TOKEN_EXPIRE_SECONDS
        return user_token_db.refresh_token(token, new_expires_at)

    def _do_register(self, user_id: str, password: str) -> UserToken:
        from src.assistant.assistant_manager import assistant_manager

        # 注册新用户
        validate_username(user_id)
        validate_password(password)

        password_hash = hash_password(password)
        if not user_db.create(user_id, password_hash):
            raise RuntimeError("用户创建失败")

        # 初始化用户 Skills（从项目根目录复制默认 Skills）
        # 失败不影响注册流程
        skills_manager.init_user_skills(user_id)

        # 初始化用户配置
        # 失败不影响注册流程
        user_config_manager.update_config(
            user_id=user_id,
            model_key=app_config.get_default_model(),
            enable_thinking=False,
        )

        # 初始化助手并发送打招呼消息
        assistant_manager.submit_chat(
            user_id=user_id,
            chat=chat_factory.create_system_remainder_chat(
                "这是你与用户的首次聊天，请向用户做个自我介绍吧。"
            ),
        )

        return self._create_token(user_id)

    def _do_login(self, user, password: str) -> UserToken:
        # 登录验证
        if not verify_password(password, user.password_hash):
            raise InvalidPasswordException()

        return self._create_token(user.user_id)

    def _create_token(self, user_id: str) -> UserToken:
        # 创建token并设置过期时间，返回token信息
        # 先清理过期token
        user_token_db.delete_expired_tokens(user_id)

        # 获取当前用户的token数量,如果超过最大限制，删除最老的token
        tokens = user_token_db.get_tokens_by_user_id(user_id)
        len_tokens = len(tokens)
        while len_tokens >= self.MAX_TOKENS_PER_USER:
            user_token_db.delete_oldest_token(user_id)
            len_tokens -= 1

        # 创建新token
        new_token = secrets.token_urlsafe(32)
        expires_at = time_util.get_timestamp() + self.TOKEN_EXPIRE_SECONDS

        if not user_token_db.create_token(user_id, new_token, expires_at):
            raise RuntimeError("Token创建失败")

        # 返回创建的token信息
        return user_token_db.get_by_token(new_token)


user_manager = _UserManager()
