"""命令行模块"""

from src.modules.base_module import BaseModule
from src.modules.shell.shell_tool import ShellTool
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook


class ShellModule(BaseModule):
    """命令行执行模块"""

    id = "shell"
    name = "命令行执行模块"
    description = "提供了shell工具使得你可以执行shell命令，这些命令将会被运行在系统的服务端，务必谨慎使用。虽然shell工具可以做很多的事情，但最好优先使用其他内置工具，因为它们提供更好的用户体验，更安全，且更容易管控权限"

    def __init__(self, user_id: str) -> None:
        """初始化命令行模块，创建工具实例"""
        self._tools: list[BaseTool] = [ShellTool(user_id)]
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
