"""写入记忆模块 Hook 实现"""

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import ConfirmedChatHook
from src.modules.memory.conversation_manager import conversation_manager


class WriteMemoryHook(ConfirmedChatHook):
    """写入记忆模块的钩子"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        """批量写入记忆模块"""
        if data:
            conversation_manager.add_chats(context.user_id, data)
        return data
