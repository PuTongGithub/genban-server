"""Chat 文件存储模块 - 负责 JSONL 文件的读写操作"""

from datetime import datetime
from pathlib import Path

from src.agent.entities import Chat
from src.common.logger import get_logger
from src.common.utils.path_util import get_user_chat_dir
from src.common.utils.time_util import STR_FORMATTER_DATE_NO_MARKS, timestamp_to_str
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

    def _timestamp_to_date_str(self, timestamp: int) -> str:
        """将时间戳转换为日期字符串

        Args:
            timestamp: 秒级时间戳

        Returns:
            日期字符串，格式 YYYYMMDD
        """
        return timestamp_to_str(timestamp, STR_FORMATTER_DATE_NO_MARKS)

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
                date_str = self._timestamp_to_date_str(chat.time)
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

    def read_chats_in_range(
        self, user_id: str, start_time: int, end_time: int
    ) -> list[dict]:
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

            # 计算需要读取的日期范围
            start_date = self._timestamp_to_date_str(start_time)
            end_date = self._timestamp_to_date_str(end_time)

            # 获取日期范围内的所有文件
            all_chats: list[dict] = []

            # 遍历可能的日期文件
            current_date = datetime.strptime(start_date, "%Y%m%d")
            end_date_obj = datetime.strptime(end_date, "%Y%m%d")

            while current_date <= end_date_obj:
                date_str = current_date.strftime("%Y%m%d")
                file_path = chat_dir / f"{date_str}.jsonl"

                if file_path.exists():
                    # 读取文件中的所有记录
                    records = file_storage.read_jsonl(file_path)
                    all_chats.extend(records)

                current_date = datetime.fromtimestamp(
                    current_date.timestamp() + 86400
                )

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


# 全局单例
chat_file_storage = ChatFileStorage()
