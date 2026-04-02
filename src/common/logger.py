"""日志工具模块

提供统一的日志记录功能，支持控制台和文件输出，自动日志轮转。
"""

import json
import logging
import logging.handlers
from pathlib import Path
from typing import Any

from src.common.utils.path_util import get_env_config_dir

# 默认日志格式
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别映射
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(config_path: Path | None = None) -> None:
    """初始化日志系统

    Args:
        config_path: 日志配置文件路径，默认根据 APP_ENV 环境变量从 config/{APP_ENV}/logging_config.json 加载
    """
    if config_path is None:
        config_path = get_env_config_dir() / "logging_config.json"

    # 加载配置
    config = _load_config(config_path)

    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL_MAP.get(config.get("level", "INFO"), logging.INFO))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL_MAP.get(config.get("level", "INFO"), logging.INFO))
    console_formatter = logging.Formatter(
        fmt=config.get("format", DEFAULT_LOG_FORMAT),
        datefmt=config.get("date_format", DEFAULT_DATE_FORMAT),
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 添加文件处理器（如果配置启用）
    if config.get("file_enabled", True):
        log_dir = Path(config.get("log_dir", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=log_dir / config.get("log_file", "app.log"),
            when=config.get("rotation_when", "midnight"),
            interval=config.get("rotation_interval", 1),
            backupCount=config.get("backup_count", 7),
            encoding="utf-8",
        )
        file_handler.setLevel(LOG_LEVEL_MAP.get(config.get("level", "INFO"), logging.INFO))
        file_formatter = logging.Formatter(
            fmt=config.get("format", DEFAULT_LOG_FORMAT),
            datefmt=config.get("date_format", DEFAULT_DATE_FORMAT),
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # 设置第三方库的日志级别
    _set_third_party_log_levels(config.get("third_party_levels", {}))


def _load_config(config_path: Path) -> dict[str, Any]:
    """加载日志配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        日志配置字典
    """
    if not config_path.exists():
        return _get_default_config()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return _get_default_config()


def _get_default_config() -> dict[str, Any]:
    """获取默认日志配置"""
    return {
        "level": "INFO",
        "format": DEFAULT_LOG_FORMAT,
        "date_format": DEFAULT_DATE_FORMAT,
        "file_enabled": True,
        "log_dir": "logs",
        "log_file": "app.log",
        "rotation_when": "midnight",
        "rotation_interval": 1,
        "backup_count": 7,
        "third_party_levels": {
            "urllib3": "WARNING",
            "httpcore": "WARNING",
        },
    }


def _set_third_party_log_levels(levels: dict[str, str]) -> None:
    """设置第三方库的日志级别

    Args:
        levels: 库名到日志级别的映射
    """
    for logger_name, level in levels.items():
        logging.getLogger(logger_name).setLevel(LOG_LEVEL_MAP.get(level, logging.WARNING))


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器

    Args:
        name: 日志记录器名称，建议使用模块的 __name__

    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)
