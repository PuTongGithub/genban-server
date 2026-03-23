"""读取对话 Hook 实现"""

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import HistoryChatsHook
from src.modules.conversation.components.conversation_manager import conversation_manager


class ReadConversationHook(HistoryChatsHook):
    """从历史记录中加载对话的钩子"""

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """从 conversation_manager 获取用户历史对话"""
        if data is None:
            data = []

        history = conversation_manager.get_combined_history(context.user_id)
        data.extend(history)

        return data
