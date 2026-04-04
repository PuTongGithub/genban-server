"""Conversation Memory 数据访问层"""

from src.common.logger import get_logger
from src.common.utils.time_util import get_timestamp
from src.storage.sqlite.database import db_execute, db_query
from src.storage.sqlite.models import ConversationMemory

logger = get_logger(__name__)


class ConversationMemoryRepository:
    """Conversation Memory 数据访问类（简化版，每个用户一条记录）"""

    @db_query
    def get_memory(self, db, user_id: str) -> ConversationMemory | None:
        """获取用户的 Conversation Memory

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            ConversationMemory 对象，不存在返回 None
        """
        return db.query(ConversationMemory).filter(ConversationMemory.user_id == user_id).first()

    @db_execute
    def save_memory(
        self,
        db,
        user_id: str,
        end_chat_id: str,
        end_chat_time: int,
        summary: str,
    ) -> ConversationMemory | None:
        """保存或更新 Conversation Memory（upsert）

        Args:
            db: 数据库会话
            user_id: 用户 ID
            end_chat_id: 最后一条被压缩的 chat ID
            end_chat_time: 最后一条被压缩的 chat 时间戳
            summary: 摘要内容

        Returns:
            保存后的 ConversationMemory 对象，失败返回 None
        """
        current_time = get_timestamp()

        # 查找现有记录
        existing = (
            db.query(ConversationMemory).filter(ConversationMemory.user_id == user_id).first()
        )

        if existing:
            # 更新现有记录
            existing.end_chat_id = end_chat_id
            existing.end_chat_time = end_chat_time
            existing.summary = summary
            existing.created_at = current_time  # 更新时间
            db.flush()

            logger.info(f"已更新 Conversation Memory: user_id={user_id}")
            return existing
        else:
            # 创建新记录
            memory = ConversationMemory(
                user_id=user_id,
                end_chat_id=end_chat_id,
                end_chat_time=end_chat_time,
                summary=summary,
                created_at=current_time,
            )

            db.add(memory)
            db.flush()  # 获取自增 ID

            logger.info(f"已创建 Conversation Memory: user_id={user_id}")
            return memory

    @db_execute
    def delete_memory(self, db, user_id: str) -> bool:
        """删除用户的 Conversation Memory

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            是否删除成功
        """
        memory = db.query(ConversationMemory).filter(ConversationMemory.user_id == user_id).first()
        if memory:
            db.delete(memory)
            logger.info(f"已删除 Conversation Memory: user_id={user_id}")
            return True
        return False


# 全局单例
conversation_memory_repository = ConversationMemoryRepository()
