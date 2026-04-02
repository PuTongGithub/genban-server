"""用户鉴权模块"""

from functools import wraps
from typing import Optional

from fastapi import Header

from src.user.exceptions import UnauthorizedException
from src.user.user_manager import user_manager


def _parse_token(authorization: Optional[str]) -> str:
    """解析并验证Authorization头，返回token

    Args:
        authorization: 请求头中的 Authorization 字段

    Returns:
        str: 解析出的token

    Raises:
        UnauthorizedException: 格式错误或缺少token时抛出
    """
    if not authorization:
        raise UnauthorizedException("缺少 Authorization 请求头")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise UnauthorizedException("Authorization 格式错误，应为 Bearer <token>")

    return token


async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """FastAPI 依赖函数：获取当前用户ID

    从请求头中读取 Authorization: Bearer <token>，验证 token 并返回 user_id

    Args:
        authorization: 请求头中的 Authorization 字段

    Returns:
        str: 验证通过的用户ID

    Raises:
        UnauthorizedException: token 无效或过期时抛出 401 异常
    """
    token = _parse_token(authorization)

    try:
        user_id = user_manager.validate_token(token)
        return user_id
    except Exception:
        raise UnauthorizedException("Token 无效或已过期")


async def get_current_user_id_and_token(
    authorization: Optional[str] = Header(None),
) -> tuple[str, str]:
    """FastAPI 依赖函数：获取当前用户ID和token

    从请求头中读取 Authorization: Bearer <token>，验证 token 并返回 user_id 和原始 token
    用于需要刷新token过期时间的场景

    Args:
        authorization: 请求头中的 Authorization 字段

    Returns:
        tuple[str, str]: (验证通过的用户ID, 原始token字符串)

    Raises:
        UnauthorizedException: token 无效或过期时抛出 401 异常
    """
    token = _parse_token(authorization)

    try:
        user_id = user_manager.validate_token(token)
        return user_id, token
    except Exception:
        raise UnauthorizedException("Token 无效或已过期")


def require_auth(func):
    """装饰器：用于非路由函数的鉴权（可选）

    注意：此装饰器适用于普通函数，FastAPI 路由函数建议使用 get_current_user_id 依赖注入

    Usage:
        @require_auth
        async def some_protected_function(token: str):
            # 函数逻辑
            pass
    """

    @wraps(func)
    async def wrapper(*args, token: Optional[str] = None, **kwargs):
        if not token:
            raise UnauthorizedException("缺少 token 参数")

        try:
            user_id = user_manager.validate_token(token)
            kwargs["current_user_id"] = user_id
            return await func(*args, **kwargs)
        except Exception:
            raise UnauthorizedException("Token 无效或已过期")

    return wrapper
