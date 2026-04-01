"""Chat 文件存储模块 - 负责 JSONL 文件的读写操作"""

from pathlib import Path

from src.agent.entities import Chat
from src.common.logger import get_logger
from src.common.utils.path_util import get_user_chat_dir
from src.common.utils.time_util import (
    get_timestamp,
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

    def _get_files_in_range(
        self,
        user_id: str,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> list[Path]:
        """获取指定时间范围内的所有 Chat 文件路径

        Args:
            user_id: 用户 ID
            start_time: 开始时间戳（秒），为 None 则不限制开始时间
            end_time: 结束时间戳（秒），为 None 则不限制结束时间）

        Returns:
            文件路径列表
        """
        chat_dir = get_user_chat_dir(user_id)

        # 获取用户目录下所有 jsonl 文件
        all_files = [f for f in chat_dir.glob("*.jsonl") if f.stem.isdigit()]

        # 按日期排序
        all_files.sort(key=lambda x: x.stem)

        # 过滤文件
        result = []
        end_date_str = None if end_time is None else timestamp_to_date_str(end_time)
        start_date_str = None if start_time is None else timestamp_to_date_str(start_time)
        for f in all_files:
            # 检查结束时间限制
            if end_date_str is not None and f.stem > end_date_str:
                continue
            # 检查开始时间限制
            if start_date_str is not None and f.stem < start_date_str:
                continue
            result.append(f)

        return result

    def _read_chats_from_files(self, files: list[Path], reverse: bool = False) -> list[dict]:
        """从文件列表中读取所有 Chat 记录

        Args:
            files: 文件路径列表

        Returns:
            Chat 字典列表
        """
        all_chats: list[dict] = []
        for file_path in files:
            records = file_storage.read_jsonl(file_path)
            all_chats.extend(records)
        if reverse:
            all_chats.reverse()
        return all_chats

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
            # 获取日期范围内的所有文件（按升序排列）
            files = self._get_files_in_range(user_id, start_time, end_time)
            all_chats = self._read_chats_from_files(files)

            # 过滤出在时间范围内的记录，并按时间排序
            filtered_chats = [
                chat for chat in all_chats if start_time <= chat.get("time", 0) <= end_time
            ]

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
            # 从 after_time 读到当前时间
            start_time = after_time

            # 获取日期范围内的所有文件（按升序排列）
            files = self._get_files_in_range(user_id, start_time=start_time)
            all_chats = self._read_chats_from_files(files)

            # 过滤出 after_chat_id 之后的记录（排除该 ID 及之前的所有内容），并按时间排序
            filtered_chats: list[dict] = []
            found = False
            for chat in all_chats:
                if found:
                    filtered_chats.append(chat)
                elif chat.get("id") == after_chat_id:
                    found = True

            logger.debug(
                f"已读取 chat_id 之后的 Chat: user_id={user_id}, "
                f"after_chat_id={after_chat_id}, after_time={after_time}, 数量={len(filtered_chats)}"
            )

            return filtered_chats
        except Exception:
            logger.exception(f"读取 chat_id 之后的 Chat 失败: user_id={user_id}")
            return []

    def read_chats_before(
        self, user_id: str, before_chat_id: str | None, before_time: int | None, count: int
    ) -> list[dict]:
        """读取指定 chat_id 和时间之前的 Chat

        Args:
            user_id: 用户 ID
            before_chat_id: 参考 chat ID，为空则返回最新的 count 条
            before_time: 参考时间戳（秒），用于确定起始日期，为空则从最新日期开始
            count: 查询数量

        Returns:
            Chat 字典列表，按时间降序排列（最新的在前）
        """
        try:
            # 确定结束时间（用于确定起始日期）
            end_time = before_time if before_time else get_timestamp()

            # 获取结束日期及之前的所有文件，按日期降序排列
            files = self._get_files_in_range(user_id, start_time=None, end_time=end_time)

            all_chats = self._read_chats_from_files(files, reverse=True)

            # 如果指定了 before_chat_id，需要先找到该 ID，然后收集它之后的数据
            chats = []
            found_before_id = before_chat_id is None  # 如果没有指定 ID，直接开始收集
            for chat in all_chats:
                if not found_before_id:
                    if chat.get("id") == before_chat_id:
                        found_before_id = True  # 找到了，下次循环开始收集
                else:
                    chats.append(chat)
                    if len(chats) >= count:
                        break

            return chats
        except Exception:
            logger.exception(f"读取 chat_id 之前的 Chat 失败: user_id={user_id}")
            return []


# 全局单例
chat_file_storage = ChatFileStorage()
