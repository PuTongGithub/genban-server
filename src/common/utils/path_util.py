"""路径工具函数"""

from pathlib import Path

from platformdirs import (
    user_cache_dir,
    user_config_dir,
    user_data_dir,
)

APP_NAME = "server"
APP_AUTHOR = "genban"


class PathNotAllowedException(Exception):
    """路径不在允许范围内异常"""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"路径 '{path}' 不在允许访问的范围内")


def get_path(path_input: str | Path) -> Path:
    """获取或创建路径"""
    path = Path(path_input)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_dir() -> Path:
    """获取配置目录"""
    return get_path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_data_dir() -> Path:
    """获取数据目录"""
    return get_path(user_data_dir(APP_NAME, APP_AUTHOR))


def get_cache_dir() -> Path:
    """获取缓存目录"""
    return get_path(user_cache_dir(APP_NAME, APP_AUTHOR))


def get_system_dir() -> Path:
    """获取系统数据目录"""
    return get_path(get_data_dir() / "system_data")


def get_user_dir(user_id: str) -> Path:
    """获取用户数据目录"""
    return get_path(get_data_dir() / "user_data" / user_id)


def get_user_files_dir(user_id: str) -> Path:
    """获取用户文件数据目录"""
    return get_path(get_user_dir(user_id) / "files")


def get_user_skills_dir(user_id: str) -> Path:
    """获取用户 Skills 目录"""
    return get_path(get_user_dir(user_id) / "skills")


def get_memory_data_dir() -> Path:
    """获取记忆数据目录"""
    return get_path(get_data_dir() / "memory_data")


def get_user_chat_dir(user_id: str) -> Path:
    """获取用户对话存储目录"""
    return get_path(get_memory_data_dir() / user_id / "chat")


def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(__file__).parent.parent.parent.parent


def get_project_skills_dir() -> Path:
    """获取项目根目录下的 Skills 目录（用于初始化用户 Skills）"""
    return get_project_root() / "skills"


def get_env_config_dir(env: str | None = None) -> Path:
    """获取环境配置目录

    Args:
        env: 环境名称，如 dev/prod，为 None 时从 APP_ENV 环境变量获取，默认为 dev

    Returns:
        配置目录路径
    """
    import os

    if env is None:
        env = os.getenv("APP_ENV", "dev")
    return get_project_root() / "config" / env
