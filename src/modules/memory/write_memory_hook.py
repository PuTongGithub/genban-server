"""写入记忆模块 Hook 实现"""

from src.agent.hooks.base_hook import ConfirmedChatHook
from src.agent.entities import Chat, AgentContext
from src.modules.memory.conversation_manager import conversation_manager


class WriteMemoryHook(ConfirmedChatHook):
    """写入记忆模块的钩子"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        """写入记忆模块的钩子"""
        conversation_manager.add_chat(context.user_id, data)
        return data
