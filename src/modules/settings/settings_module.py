"""配置模块"""

from src.modules.base_module import BaseModule
from src.agent.tools.base_tool import BaseTool
from src.agent.hooks.base_hook import BaseHook
from src.modules.settings.setting_tool import SettingTool
from src.modules.settings.setting_model_hook import SettingModelHook


class SettingsModule(BaseModule):
    """用户配置模块"""

    id = "settings"
    name = "用户配置模块"
    description = "提供了用户配置的管理能力，你可以通过调用工具去修改当前用户的配置，用户也可以通过客户端界面自行操作修改配置"

    def __init__(self) -> None:
        """初始化配置模块，创建工具实例"""
        self._tools: list[BaseTool] = [SettingTool()]
        self._hooks: list[BaseHook] = [SettingModelHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
