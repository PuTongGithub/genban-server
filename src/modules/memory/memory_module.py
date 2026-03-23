"""记忆模块

提供长期记忆存储和检索功能
"""

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool
from src.modules.base_module import BaseModule


class MemoryModule(BaseModule):
    """记忆模块

    负责长期记忆的存储、检索和管理
    """

    id = "memory"
    name = "记忆模块"
    description = "提供长期记忆存储和检索功能"
    message_tag = None
    message_tag_instruction = None

    def __init__(self) -> None:
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
