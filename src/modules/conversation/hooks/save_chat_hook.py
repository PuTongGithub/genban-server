"""保存对话 Hook 实现"""

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import ConfirmedChatHook
from src.modules.conversation.chat.chat_repository import chat_repository


class SaveChatHook(ConfirmedChatHook):
    """将对话追加写入文件存储的钩子"""

    order = 1  # 优先执行，确保先保存再触发其他逻辑

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """批量写入对话到文件存储"""
        if not data:
            return data

        chat_repository.save_chats(context.user_id, data)
        return data
