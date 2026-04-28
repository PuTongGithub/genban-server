"""写入对话 Hook 实现"""

import threading

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import ConfirmedChatHook
from src.common.logger import get_logger
from src.modules.conversation.components.conversation_manager import conversation_manager

logger = get_logger(__name__)


class WriteConversationHook(ConfirmedChatHook):
    """写入对话并触发压缩的钩子"""

    order = 100  # 在 SaveChatHook 之后执行
    async_execute = True  # 异步执行

    def __init__(self) -> None:
        self._compression_locks: dict[str, threading.Lock] = {}

    def _get_lock(self, user_id: str) -> threading.Lock:
        """获取 user_id 维度的压缩锁

        Args:
            user_id: 用户 ID

        Returns:
            该用户对应的 threading.Lock
        """
        if user_id not in self._compression_locks:
            self._compression_locks[user_id] = threading.Lock()
        return self._compression_locks[user_id]

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """检查并触发上下文压缩"""
        if not data:
            return data

        # 只有本轮对话完成时才触发压缩判断，避免在工具调用链中间触发压缩
        if not context.process_result:
            return data

        # 检查是否需要触发压缩（只检查 max_token）
        if not conversation_manager.should_compress(context.total_tokens):
            return data

        user_id = context.user_id
        lock = self._get_lock(user_id)

        # 尝试获取锁，如果失败说明已有压缩在进行中，直接返回
        if not lock.acquire(timeout=0):
            logger.info(f"压缩任务已在执行，跳过本次触发: user_id={user_id}")
            return data

        try:
            # 获取当前最新的 chat_id
            current_chat_id = conversation_manager.get_current_memory_chat_id(user_id)
            context_chat_id = context.history_chats[0].id
            # 校验 chat_id 是否一致，不一致则跳过压缩
            if context_chat_id != current_chat_id:
                logger.info(
                    f"conversation 状态已变更，跳过本次压缩: "
                    f"user_id={user_id}, context_chat_id={context_chat_id}, current_chat_id={current_chat_id}"
                )
                return

            # 执行压缩
            conversation_manager.compress_context(context)
        except Exception:
            logger.exception(f"异步压缩执行失败: user_id={user_id}")
        finally:
            lock.release()

        return data