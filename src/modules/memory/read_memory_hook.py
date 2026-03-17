"""读取记忆模块 Hook 实现"""

from src.agent.hooks.base_hook import HistoryChatsHook
from src.agent.entities import Chat, AgentContext
from src.modules.memory.conversation_manager import conversation_manager


class ReadMemoryHook(HistoryChatsHook):
    """从历史记录中加载对话的钩子"""

    def execute(
        self, data: list[Chat] | None, context: AgentContext
    ) -> list[Chat] | None:
        """从 conversation_manager 获取用户历史对话"""
        if data is None:
            data = []

        history = conversation_manager.get_history(context.user_id)
        data.extend(history)

        return data
