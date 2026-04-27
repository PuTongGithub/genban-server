"""用户鉴权模块"""

from pathlib import Path
from typing import Optional

from fastapi import Header, Request

from src.common.utils.path_util import PathNotAllowedException, get_user_dir
from src.config.config import app_config
from src.user.exceptions import UnauthorizedException
from src.user.user_manager import user_manager

# Cookie 名称常量
SESSION_COOKIE_NAME = "session"


def _get_token_from_cookie(request: Request) -> Optional[str]:
    """从 Cookie 中获取 session token

    Args:
        request: FastAPI 请求对象

    Returns:
        Optional[str]: Cookie 中的 session token，如果没有则返回 None
    """
    return request.cookies.get(SESSION_COOKIE_NAME)


def _parse_token(authorization: Optional[str]) -> Optional[str]:
    """解析并验证Authorization头，返回token

    Args:
        authorization: 请求头中的 Authorization 字段

    Returns:
        Optional[str]: 解析出的token，如果格式错误则返回 None
    """
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token


def _get_token_from_request(request: Request, authorization: Optional[str]) -> str:
    """从请求中获取 token，优先从 Cookie 获取，其次从 Authorization Header 获取

    Args:
        request: FastAPI 请求对象
        authorization: 请求头中的 Authorization 字段

    Returns:
        str: 获取到的 token

    Raises:
        UnauthorizedException: 无法获取有效 token 时抛出
    """
    # 优先从 Cookie 获取
    cookie_token = _get_token_from_cookie(request)
    if cookie_token:
        return cookie_token

    # 其次从 Authorization Header 获取
    header_token = _parse_token(authorization)
    if header_token:
        return header_token

    raise UnauthorizedException("未提供有效的认证信息")


async def get_current_user_id(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> str:
    """FastAPI 依赖函数：获取当前用户ID

    优先从 Cookie 中获取 session，其次从 Authorization Header 获取 token
    验证 token/session 并返回 user_id

    Args:
        request: FastAPI 请求对象
        authorization: 请求头中的 Authorization 字段

    Returns:
        str: 验证通过的用户ID

    Raises:
        UnauthorizedException: token/session 无效或过期时抛出 401 异常
    """
    token = _get_token_from_request(request, authorization)

    try:
        user_id = user_manager.validate_token(token)
        return user_id
    except Exception:
        raise UnauthorizedException("认证信息无效或已过期")


async def get_current_user_id_and_token(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> tuple[str, str]:
    """FastAPI 依赖函数：获取当前用户ID和token

    优先从 Cookie 中获取 session，其次从 Authorization Header 获取 token
    验证 token/session 并返回 user_id 和原始 token
    用于需要刷新token过期时间的场景

    Args:
        request: FastAPI 请求对象
        authorization: 请求头中的 Authorization 字段

    Returns:
        tuple[str, str]: (验证通过的用户ID, 原始token字符串)

    Raises:
        UnauthorizedException: token/session 无效或过期时抛出 401 异常
    """
    token = _get_token_from_request(request, authorization)

    try:
        user_id = user_manager.validate_token(token)
        return user_id, token
    except Exception:
        raise UnauthorizedException("认证信息无效或已过期")


def validate_path(path: str, user_id: str) -> Path:
    """验证路径是否在用户允许的范围内，返回绝对路径

    允许访问的目录：
    - 用户目录下所有内容: {data_dir}/user_data/{user_id}
    - 管理员用户可访问任意路径

    Args:
        path: 相对路径或绝对路径
        user_id: 用户ID

    Returns:
        验证通过的绝对路径

    Raises:
        PathNotAllowedException: 路径不在允许范围内
    """
    user_dir = get_user_dir(user_id)

    user_dir.mkdir(parents=True, exist_ok=True)

    if Path(path).is_absolute():
        target_path = Path(path).resolve()
    else:
        target_path = (user_dir / path).resolve()

    if user_id in app_config.get_admin_user_ids():
        return target_path
    try:
        target_path.relative_to(user_dir)
        return target_path
    except ValueError:
        raise PathNotAllowedException(str(path))

def get_relative_path(path: Path, user_id: str) -> str:
    """获取路径相对于用户目录的相对路径

    Args:
        path: 绝对路径
        user_id: 用户ID

    Returns:
        相对路径字符串（使用正斜杠 / 作为分隔符）
    """
    user_dir = get_user_dir(user_id)
    relative_path = path.relative_to(user_dir)
    return relative_path.as_posix()