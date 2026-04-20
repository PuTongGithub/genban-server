"""获取用户配置工具"""

from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.common.logger import get_logger
from src.user.user_config_manager import user_config_manager

logger = get_logger(__name__)


class SettingGetTool(BaseTool):
    """获取用户配置工具"""

    name = "setting_get"
    description = "获取当前用户的配置信息，包括模型选择和深度思考开关状态"
    parameters = []

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行获取用户配置操作

        Args:
            context: Agent 执行上下文

        Returns:
            当前配置信息
        """
        user_id = context.user_id
        config = user_config_manager.get_config(user_id)

        logger.info(f"获取用户配置成功，user_id: {user_id}, model_key: {config.model_key}, enable_thinking: {config.enable_thinking}")

        thinking_status = "开启" if config.enable_thinking else "关闭"
        return f"当前配置：模型为 {config.model_key}，深度思考模式{thinking_status}"
