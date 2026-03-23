"""对话模块

提供对话上下文管理和压缩功能
"""

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool
from src.modules.base_module import BaseModule
from src.modules.conversation.hooks.read_conversation_hook import ReadConversationHook
from src.modules.conversation.hooks.save_chat_hook import SaveChatHook
from src.modules.conversation.hooks.write_conversation_hook import WriteConversationHook


class ConversationModule(BaseModule):
    """对话模块"""

    id = "conversation"
    name = "对话模块"
    description = "提供对话上下文管理能力，在上下文超过指定长度时会自动压缩"
    message_tag = "[conversation]"
    message_tag_instruction = "标签后跟压缩后的对话内容摘要"

    def __init__(self) -> None:
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = [
            ReadConversationHook(),
            SaveChatHook(),
            WriteConversationHook(),
        ]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
