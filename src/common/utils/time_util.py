"""时间工具函数"""

import time
from datetime import datetime, timedelta
from typing import Iterator

ONE_MINUTE_SECOND = 60
ONE_HOUR_SECOND = 60 * ONE_MINUTE_SECOND
ONE_DAY_SECOND = 24 * ONE_HOUR_SECOND

STR_FORMATTER_NO_MARKS = "%Y%m%d%H%M%S"
STR_FORMATTER_WITH_MARKS = "%Y-%m-%d %H:%M:%S"
STR_FORMATTER_DATE_NO_MARKS = "%Y%m%d"
STR_FORMATTER_DATE_WITH_MARKS = "%Y-%m-%d"


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


def timestamp_to_date_str(timestamp: int) -> str:
    """时间戳转日期字符串（YYYYMMDD）"""
    return datetime.fromtimestamp(timestamp).strftime(STR_FORMATTER_DATE_NO_MARKS)


def date_str_to_datetime(date_str: str) -> datetime:
    """日期字符串（YYYYMMDD）转 datetime"""
    return datetime.strptime(date_str, STR_FORMATTER_DATE_NO_MARKS)


def datetime_to_date_str(dt: datetime) -> str:
    """datetime 转日期字符串（YYYYMMDD）"""
    return dt.strftime(STR_FORMATTER_DATE_NO_MARKS)


def iterate_date_range(start_date_str: str, end_date_str: str) -> Iterator[str]:
    """遍历日期范围内的所有日期字符串

    Args:
        start_date_str: 开始日期字符串（YYYYMMDD）
        end_date_str: 结束日期字符串（YYYYMMDD）

    Yields:
        日期字符串（YYYYMMDD）
    """
    current = datetime.strptime(start_date_str, STR_FORMATTER_DATE_NO_MARKS)
    end = datetime.strptime(end_date_str, STR_FORMATTER_DATE_NO_MARKS)

    while current <= end:
        yield current.strftime(STR_FORMATTER_DATE_NO_MARKS)
        current += timedelta(days=1)


def iterate_date_range_by_timestamp(start_timestamp: int, end_timestamp: int) -> Iterator[str]:
    """根据时间戳遍历日期范围内的所有日期字符串

    Args:
        start_timestamp: 开始时间戳
        end_timestamp: 结束时间戳

    Yields:
        日期字符串（YYYYMMDD）
    """
    start_date = timestamp_to_date_str(start_timestamp)
    end_date = timestamp_to_date_str(end_timestamp)
    yield from iterate_date_range(start_date, end_date)
