"""记忆模块"""

from src.modules.base_module import BaseModule
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook
from src.modules.memory.read_memory_hook import ReadMemoryHook
from src.modules.memory.write_memory_hook import WriteMemoryHook


class MemoryModule(BaseModule):
    """记忆模块"""

    id = "memory"
    name = "记忆模块(目前未实装)"
    description = "提供了对用户记忆的管理能力"
    message_tag = "[memory]"
    message_tag_instruction = "标签后跟记忆内容"

    def __init__(self) -> None:
        self._tools: list[BaseTool] = []
        self._hooks: list[BaseHook] = [ReadMemoryHook(), WriteMemoryHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
