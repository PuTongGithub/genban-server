"""IM 凭证管理模块"""

from src.agent.hooks.base_hook import BaseHook
from src.agent.tools.base_tool import BaseTool
from src.modules.base_module import BaseModule
from src.modules.im.hooks.im_confirmed_chat_hook import IMConfirmedChatHook
from src.modules.im.tool.im_create_tool import IMCreateTool
from src.modules.im.tool.im_list_tool import IMListTool
from src.modules.im.tool.im_update_tool import IMUpdateTool


class IMModule(BaseModule):
    """IM 管理模块"""

    id = "im"
    name = "IM管理模块"
    description = (
        "除了客户端外，系统还另外支持用户使用不同IM渠道与你交流，该模块提供IM渠道相关的配置管理能力"
    )

    def __init__(self) -> None:
        self._tools: list[BaseTool] = [IMListTool(), IMCreateTool(), IMUpdateTool()]
        self._hooks: list[BaseHook] = [IMConfirmedChatHook()]

    def get_tools(self) -> list[BaseTool]:
        return self._tools

    def get_hooks(self) -> list[BaseHook]:
        return self._hooks
