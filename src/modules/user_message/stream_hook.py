"""Stream Hook 实现 - StreamNewChatHook"""

from src.agent.hooks.base_hook import NewChatHook
from src.agent.entities import Chat, AgentContext
from src.modules.user_message.stream_manager import stream_manager


class StreamHook(NewChatHook):
    """NewChatHook 实现，将新 Chat 推送到 SSE 流"""

    def execute(self, data: Chat | None, context: AgentContext) -> Chat | None:
        """执行钩子：将新 Chat 推送到对应用户的 SSE 流"""
        if data is None:
            return None

        # 推送到对应用户的 SSE 流
        stream_manager.push_chat(context.user_id, data)

        return data
