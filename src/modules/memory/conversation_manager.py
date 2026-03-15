"""对话上下文管理器 - 内存存储"""

from src.agent.entities import Chat


class ConversationManager:
    """管理用户的对话上下文（内存存储）"""

    def __init__(self):
        # 用户对话历史: {user_id: [Chat, Chat, ...]}
        self._conversations: dict[str, list[Chat]] = {}

    def get_history(self, user_id: str) -> list[Chat]:
        """获取用户的历史对话"""
        return self._conversations.get(user_id, [])

    def add_chat(self, user_id: str, chat: Chat) -> None:
        """添加对话到用户历史"""
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        self._conversations[user_id].append(chat)

    def add_chats(self, user_id: str, chats: list[Chat]) -> None:
        """批量添加对话到用户历史"""
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        self._conversations[user_id].extend(chats)

    def clear_history(self, user_id: str) -> None:
        """清空用户对话历史"""
        if user_id in self._conversations:
            self._conversations[user_id] = []

    def get_all_user_ids(self) -> list[str]:
        """获取所有用户ID"""
        return list(self._conversations.keys())


# 全局单例
conversation_manager = ConversationManager()
