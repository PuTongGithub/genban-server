"""对话上下文管理器

管理用户的对话上下文，包括：
- Chat 的读写（基于文件存储）
- Conversation Memory 的读写（基于 SQLite）
- 上下文压缩的触发和执行
"""

from src.agent.chat_factory import chat_factory
from src.agent.entities import AgentContext, Chat
from src.common.logger import get_logger
from src.config.config import app_config
from src.modules.conversation.chat.chat_repository import chat_repository
from src.modules.conversation.components.context_compressor import context_compressor
from src.modules.conversation.components.conversation_repository import conversation_repository

logger = get_logger(__name__)


class ConversationManager:
    """管理用户的对话上下文"""

    def should_compress(self, total_tokens: int) -> bool:
        """检查是否应该触发压缩

        Args:
            total_tokens: 当前对话总 token 数

        Returns:
            是否应该压缩（超过 max_token）
        """
        max_token = app_config.get("conversation_memory", {}).get("max_token", 10000)

        return total_tokens >= max_token

    def compress_context(self, context: AgentContext) -> None:
        """执行上下文压缩

        Args:
            context: Agent上下文
        """
        # 获取用户的历史对话
        chats = context.history_chats + context.new_chats

        # 执行压缩
        result = context_compressor.compress(context.user_id, chats)

        # 保存到数据库
        conversation_repository.save_memory(
            user_id=context.user_id,
            end_chat_id=result.end_chat_id,
            end_chat_time=result.end_chat_time,
            summary=result.summary,
        )

        logger.info(f"上下文压缩完成: user_id={context.user_id}, end_chat_id={result.end_chat_id}")

    def get_combined_history(self, user_id: str) -> list[Chat]:
        """获取组合的历史对话（memory + chat）

        Args:
            user_id: 用户 ID

        Returns:
            Chat 列表，按时间升序排列
        """
        memory = conversation_repository.get_memory(user_id)

        if memory:
            recent_chats = chat_repository.get_chats_after(
                user_id, memory.end_chat_id, memory.end_chat_time
            )
            memory_chat = chat_factory.create_conversation_chat(memory.summary)
            result = [memory_chat] + recent_chats
        else:
            recent_chats = chat_repository.get_recent_chats(user_id)
            result = recent_chats

        return result


# 全局单例
conversation_manager = ConversationManager()
