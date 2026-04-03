"""用户鉴权模块"""

from pathlib import Path
from typing import Optional

from fastapi import Header

from src.common.utils.path_util import PathNotAllowedException, get_user_dir
from src.config.config import app_config
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
