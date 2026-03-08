"""用户验证工具（包含用户名和密码校验）"""

import re
import bcrypt

from src.user.exceptions import WeakPasswordException, InvalidUsernameException


def hash_password(password: str) -> str:
    """生成密码哈希"""
    passwordBytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwordBytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, passwordHash: str) -> bool:
    """校验密码"""
    passwordBytes = password.encode("utf-8")
    hashBytes = passwordHash.encode("utf-8")
    return bcrypt.checkpw(passwordBytes, hashBytes)


def validate_password(password: str) -> None:
    """校验密码强度"""
    if len(password) < 6:
        raise WeakPasswordException("密码最少需要6位字符")


def validate_username(username: str) -> None:
    """校验用户名格式

    仅允许字母、数字、下划线

    Args:
        username: 用户名

    Raises:
        InvalidUsernameException: 用户名格式不合法
    """
    if not username:
        raise InvalidUsernameException("用户名不能为空")

    # 仅允许字母、数字、下划线
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise InvalidUsernameException("用户名只能包含字母、数字、下划线")
