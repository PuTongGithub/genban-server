"""Chats Hook 实现"""

from src.agent.hooks.base_hook import ChatsHook
from src.agent.entities import Chat, AgentContext
from src.assistant.conversation_manager import conversation_manager


class HistoryChatsHook(ChatsHook):
    """从历史记录中加载对话的钩子"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        """从 conversation_manager 获取用户历史对话"""
        history = conversation_manager.get_history(context.user_id)
        return history if history else []
