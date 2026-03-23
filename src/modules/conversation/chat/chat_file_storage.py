"""Chat 文件存储模块 - 负责 JSONL 文件的读写操作"""

from pathlib import Path

from src.agent.entities import Chat
from src.common.logger import get_logger
from src.common.utils.path_util import get_user_chat_dir
from src.common.utils.time_util import (
    get_timestamp,
    iterate_date_range_by_timestamp,
    timestamp_to_date_str,
)
from src.storage.file.file_storage import file_storage

logger = get_logger(__name__)


class ChatFileStorage:
    """Chat 文件存储类，负责 JSONL 文件的读写"""

    def _get_chat_file_path(self, user_id: str, date_str: str) -> Path:
        """获取指定日期的 Chat 文件路径

        Args:
            user_id: 用户 ID
            date_str: 日期字符串，格式 YYYYMMDD

        Returns:
            Chat 文件路径
        """
        chat_dir = get_user_chat_dir(user_id)
        return chat_dir / f"{date_str}.jsonl"

    def append_chats(self, user_id: str, chats: list[Chat]) -> None:
        """批量追加 Chat 到文件，按日期分组处理

        Args:
            user_id: 用户 ID
            chats: Chat 对象列表
        """
        if not chats:
            return

        try:
            # 按日期分组
            chats_by_date: dict[str, list[Chat]] = {}
            for chat in chats:
                date_str = timestamp_to_date_str(chat.time)
                if date_str not in chats_by_date:
                    chats_by_date[date_str] = []
                chats_by_date[date_str].append(chat)

            # 批量写入各日期文件
            for date_str, date_chats in chats_by_date.items():
                file_path = self._get_chat_file_path(user_id, date_str)
                chat_dicts = [chat.to_dict() for chat in date_chats]
                file_storage.append_to_jsonl(file_path, chat_dicts)

            logger.debug(
                f"已批量保存 Chat 到文件: user_id={user_id}, "
                f"数量={len(chats)}, 涉及日期={list(chats_by_date.keys())}"
            )
        except Exception:
            logger.exception(f"批量保存 Chat 到文件失败: user_id={user_id}, 数量={len(chats)}")
            raise

    def read_chats_in_range(self, user_id: str, start_time: int, end_time: int) -> list[dict]:
        """按时间范围读取 Chat

        Args:
            user_id: 用户 ID
            start_time: 开始时间戳（秒）
            end_time: 结束时间戳（秒）

        Returns:
            Chat 字典列表，按时间升序排列
        """
        try:
            chat_dir = get_user_chat_dir(user_id)

            # 获取日期范围内的所有文件
            all_chats: list[dict] = []

            for date_str in iterate_date_range_by_timestamp(start_time, end_time):
                file_path = chat_dir / f"{date_str}.jsonl"
                if file_path.exists():
                    records = file_storage.read_jsonl(file_path)
                    all_chats.extend(records)

            # 过滤出在时间范围内的记录，并按时间排序
            filtered_chats = [
                chat for chat in all_chats if start_time <= chat.get("time", 0) <= end_time
            ]
            filtered_chats.sort(key=lambda x: x.get("time", 0))

            logger.debug(
                f"已读取 Chat 记录: user_id={user_id}, "
                f"时间范围=[{start_time}, {end_time}], 数量={len(filtered_chats)}"
            )

            return filtered_chats
        except Exception:
            logger.exception(f"读取 Chat 记录失败: user_id={user_id}")
            return []

    def read_chats_after(self, user_id: str, after_chat_id: str, after_time: int) -> list[dict]:
        """读取指定 chat_id 和时间之后的 Chat

        Args:
            user_id: 用户 ID
            after_chat_id: 参考 chat ID
            after_time: 参考时间戳（秒），用于确定起始日期

        Returns:
            Chat 字典列表，按时间升序排列
        """
        try:
            chat_dir = get_user_chat_dir(user_id)

            # 从 after_time 读到当前时间
            start_time = after_time
            end_time = get_timestamp()

            # 获取日期范围内的所有文件
            all_chats: list[dict] = []

            for date_str in iterate_date_range_by_timestamp(start_time, end_time):
                file_path = chat_dir / f"{date_str}.jsonl"
                if file_path.exists():
                    records = file_storage.read_jsonl(file_path)
                    all_chats.extend(records)

            # 过滤出 after_chat_id 之后的记录（排除该 ID 及之前的所有内容），并按时间排序
            filtered_chats: list[dict] = []
            found = False
            for chat in sorted(all_chats, key=lambda x: x.get("time", 0)):
                if found:
                    filtered_chats.append(chat)
                elif chat.get("id") == after_chat_id:
                    found = True

            # 按时间排序
            filtered_chats.sort(key=lambda x: x.get("time", 0))

            logger.debug(
                f"已读取 chat_id 之后的 Chat: user_id={user_id}, "
                f"after_chat_id={after_chat_id}, after_time={after_time}, 数量={len(filtered_chats)}"
            )

            return filtered_chats
        except Exception:
            logger.exception(f"读取 chat_id 之后的 Chat 失败: user_id={user_id}")
            return []


# 全局单例
chat_file_storage = ChatFileStorage()
