"""用户消息模块"""

from src.modules.base_module import BaseModule
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook
from src.modules.user_message.stream_hook import StreamHook


class UserMessageModule(BaseModule):
    """用户消息模块"""

    id = "user-message"
    name = "用户消息模块"
    description = "用户在客户端上通过对话页面输入并发送消息，你将会接收到这些消息"
    message_tag = "[user:xxx:yyyy-yy-yy hh:mm:ss]"
    message_tag_instruction = "标签后跟用户消息内容，标签中的xxx表示用户id，标签中的yyyy-yy-yy hh:mm:ss表示用户发送消息的时间"

    def __init__(self) -> None:
        """初始化用户消息模块"""
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = [StreamHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
