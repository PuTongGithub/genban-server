"""对话上下文管理器 - 基于文件存储"""

from src.agent.entities import Chat
from src.common.logger import get_logger
from src.modules.memory.chat.chat_repository import chat_repository

logger = get_logger(__name__)


class ConversationManager:
    """管理用户的对话上下文（基于文件存储）"""

    def __init__(self):
        self._repository = chat_repository

    def get_history(self, user_id: str) -> list[Chat]:
        """获取用户最近24小时的历史对话

        Args:
            user_id: 用户 ID

        Returns:
            Chat 列表，按时间升序排列
        """
        return self._repository.get_recent_chats(user_id, hours=24)

    def add_chats(self, user_id: str, chats: list[Chat]) -> None:
        """批量添加对话到用户历史并持久化到文件

        Args:
            user_id: 用户 ID
            chats: Chat 列表
        """
        if not chats:
            return

        try:
            self._repository.save_chats(user_id, chats)
            logger.debug(f"已批量添加 Chat: user_id={user_id}, 数量={len(chats)}")
        except Exception:
            logger.exception(f"批量添加 Chat 失败: user_id={user_id}, 数量={len(chats)}")
            raise


# 全局单例
conversation_manager = ConversationManager()
