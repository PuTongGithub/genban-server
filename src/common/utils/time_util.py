"""时间工具函数"""

from datetime import datetime
import time


ONE_MINUTE_SECOND = 60
ONE_HOUR_SECOND = 60 * ONE_MINUTE_SECOND
ONE_DAY_SECOND = 24 * ONE_HOUR_SECOND

STR_FORMATTER_NO_MARKS = "%Y%m%d%H%M%S"
STR_FORMATTER_WITH_MARKS = "%Y-%m-%d %H:%M:%S"
STR_FORMATTER_DATE_NO_MARKS = "%Y%m%d"


def get_now() -> datetime:
    """获取当前时间"""
    return datetime.now()


def get_timestamp() -> int:
    """获取当前时间戳"""
    return int(time.time())


def get_yesterday_timestamp() -> int:
    """获取昨天时间戳"""
    return get_timestamp() - ONE_DAY_SECOND


def get_now_str(formatter: str) -> str:
    """获取当前时间字符串"""
    return get_now().strftime(formatter)


def timestamp_to_str(timestamp: int, formatter: str) -> str:
    """时间戳转字符串"""
    return datetime.fromtimestamp(timestamp).strftime(formatter)
