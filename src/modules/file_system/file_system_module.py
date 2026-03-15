"""文件系统模块"""

from src.modules.base_module import BaseModule
from src.modules.file_system.tools.read_file_tool import ReadFileTool
from src.modules.file_system.tools.write_file_tool import WriteFileTool
from src.modules.file_system.tools.edit_file_tool import EditFileTool
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook


class FileSystemModule(BaseModule):
    """文件系统模块"""

    id = "file-system"
    name = "文件系统模块"
    description = "提供了对系统服务器内用户目录下的文件的操作能力。用户可以通过客户端界面看到用户目录下的文件。请注意：你只有对用户目录下的文件进行操作的权限"

    def __init__(self) -> None:
        """初始化文件系统模块，创建工具实例"""
        self._tools: list[BaseTool] = [
            ReadFileTool(),
            WriteFileTool(),
            EditFileTool(),
        ]
        self._hooks: list[BaseHook] = []

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
