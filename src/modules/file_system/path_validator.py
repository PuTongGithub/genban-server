"""路径权限验证工具"""

from pathlib import Path
from src.common.utils.path_util import get_data_dir
from src.modules.file_system.exceptions import PathNotAllowedException


def get_user_base_dir(user_id: str) -> Path:
    """获取用户的基础目录路径"""
    return get_data_dir() / "files" / user_id


def validate_path(path: str, user_id: str) -> Path:
    """验证路径是否在用户允许的范围内，返回绝对路径

    Args:
        path: 相对路径或绝对路径
        user_id: 用户ID

    Returns:
        验证通过的绝对路径

    Raises:
        PathNotAllowedException: 路径不在允许范围内
    """
    base_dir = get_user_base_dir(user_id)
    base_dir.mkdir(parents=True, exist_ok=True)

    # 处理路径
    if Path(path).is_absolute():
        target_path = Path(path).resolve()
    else:
        target_path = (base_dir / path).resolve()

    # 验证路径是否在用户目录下
    try:
        target_path.relative_to(base_dir)
    except ValueError:
        raise PathNotAllowedException(str(path))

    return target_path
