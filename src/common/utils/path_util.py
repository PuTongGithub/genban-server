"""路径工具函数"""

from pathlib import Path
from platformdirs import (
    user_config_dir,
    user_data_dir,
    user_cache_dir,
    user_log_dir,
    user_documents_dir,
    user_downloads_dir,
    user_desktop_dir,
    user_pictures_dir,
    user_videos_dir,
    user_music_dir
)


APP_NAME = "server"
APP_AUTHOR = "genban"


def get_path(path_str: str) -> Path:
    """获取或创建路径"""
    path = Path(path_str)
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


def get_log_dir() -> Path:
    """获取日志目录"""
    return get_path(user_log_dir(APP_NAME, APP_AUTHOR))


def get_app_dirs() -> list:
    """获取所有应用目录"""
    return [
        user_config_dir(APP_NAME, APP_AUTHOR),
        user_data_dir(APP_NAME, APP_AUTHOR),
        user_cache_dir(APP_NAME, APP_AUTHOR),
        user_log_dir(APP_NAME, APP_AUTHOR)
    ]


def get_user_dirs() -> list:
    """获取所有用户目录"""
    return [
        user_documents_dir(),
        user_downloads_dir(),
        user_desktop_dir(),
        user_pictures_dir(),
        user_videos_dir(),
        user_music_dir()
    ]


def validate_path(path: str, whitelist: list) -> bool:
    """验证路径是否在白名单中"""
    return any(path.startswith(whitelist_item) for whitelist_item in whitelist)
