"""系统消息模块"""

from src.modules.base_module import BaseModule
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook
from src.modules.system_remainder.prompt_hook import PromptSetupHook


class SystemRemainderModule(BaseModule):
    """系统消息模块"""

    id = "system_remainder"
    name = "系统消息模块"
    description = "系统会向你发送一些提示或错误信息。你需要理解它们，但最好不要让用户感知到这些信息"
    message_tag = "[system_remainder]"
    message_tag_instruction = "标签后跟系统消息内容"

    def __init__(self) -> None:
        """初始化系统消息模块"""
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = [PromptSetupHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
