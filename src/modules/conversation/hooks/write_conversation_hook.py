"""写入对话 Hook 实现"""

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import ConfirmedChatHook
from src.common.logger import get_logger
from src.modules.conversation.components.conversation_manager import conversation_manager

logger = get_logger(__name__)


class WriteConversationHook(ConfirmedChatHook):
    """写入对话并触发压缩的钩子"""

    order = 100  # 在 SaveChatHook 之后执行

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """检查并触发上下文压缩"""
        if not data:
            return data

        # 只有本轮对话完成时才触发压缩判断，避免在工具调用链中间触发压缩
        if not context.process_result:
            return data

        # 检查是否需要触发压缩（只检查 max_token）
        if conversation_manager.should_compress(context.total_tokens):
            # 执行压缩，避免阻塞主流程
            conversation_manager.compress_context(context)

        return data
