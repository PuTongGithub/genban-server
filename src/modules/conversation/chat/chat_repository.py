"""Chat 数据访问层 - 封装 Chat 的存储和读取逻辑"""

from src.agent.entities import Chat
from src.common.logger import get_logger
from src.common.utils.time_util import get_timestamp
from src.modules.conversation.chat.chat_file_storage import chat_file_storage

logger = get_logger(__name__)


class ChatRepository:
    """Chat 数据访问类，提供追加写和按时间范围读取功能"""

    def save_chats(self, user_id: str, chats: list[Chat]) -> None:
        """批量保存 Chat 到文件系统

        Args:
            user_id: 用户 ID
            chats: Chat 对象列表
        """
        if not chats:
            return

        try:
            chat_file_storage.append_chats(user_id, chats)
            logger.debug(f"已批量保存 Chat: user_id={user_id}, 数量={len(chats)}")
        except Exception:
            logger.exception(f"批量保存 Chat 失败: user_id={user_id}, 数量={len(chats)}")
            raise

    def get_recent_chats(self, user_id: str, hours: int = 24) -> list[Chat]:
        """获取最近 N 小时的 Chat

        Args:
            user_id: 用户 ID
            hours: 小时数，默认 24 小时

        Returns:
            Chat 对象列表，按时间升序排列
        """
        try:
            # 计算时间范围
            end_time = get_timestamp()
            start_time = end_time - (hours * 3600)

            # 从文件读取数据
            chat_dicts = chat_file_storage.read_chats_in_range(
                user_id, start_time, end_time
            )

            # 使用 Chat.from_dict 反序列化
            chats = [Chat.from_dict(chat_dict) for chat_dict in chat_dicts]

            logger.debug(
                f"已获取最近 {hours} 小时 Chat: user_id={user_id}, 数量={len(chats)}"
            )

            return chats
        except Exception:
            logger.exception(f"获取最近 Chat 失败: user_id={user_id}")
            return []

    def get_chats_after(
        self, user_id: str, after_chat_id: str, after_time: int
    ) -> list[Chat]:
        """获取指定 chat_id 和时间之后的 Chat

        Args:
            user_id: 用户 ID
            after_chat_id: 参考 chat ID
            after_time: 参考时间戳（秒）

        Returns:
            Chat 对象列表，按时间升序排列
        """
        try:
            # 从文件读取数据
            chat_dicts = chat_file_storage.read_chats_after(
                user_id, after_chat_id, after_time
            )

            # 使用 Chat.from_dict 反序列化
            chats = [Chat.from_dict(chat_dict) for chat_dict in chat_dicts]

            logger.debug(
                f"已获取 chat_id 之后的 Chat: user_id={user_id}, "
                f"after_chat_id={after_chat_id}, after_time={after_time}, 数量={len(chats)}"
            )

            return chats
        except Exception:
            logger.exception(f"获取 chat_id 之后的 Chat 失败: user_id={user_id}")
            return []


# 全局单例
chat_repository = ChatRepository()
