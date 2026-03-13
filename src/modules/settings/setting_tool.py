"""更新用户配置工具"""

from typing import Any

from src.agent.tools.base_tool import BaseTool
from src.agent.entities import ToolParameter, AgentContext
from src.user.user_config_manager import user_config_manager
from src.common.logger import get_logger
from src.config.config import app_config

logger = get_logger(__name__)


class SettingTool(BaseTool):
    """更新用户配置工具"""

    name = "setting"
    description = "更新用户配置，包括模型选择和深度思考开关"
    parameters = [
        ToolParameter(
            name="model_key",
            type="string",
            description="要使用的模型 key",
            enum=list(app_config.get("models").keys()),
            required=False,
        ),
        ToolParameter(
            name="enable_thinking",
            type="boolean",
            description="是否开启深度思考模式",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行更新用户配置操作

        Args:
            context: Agent 执行上下文
            model_key: 要使用的模型 key
            enable_thinking: 是否开启深度思考模式

        Returns:
            更新结果消息
        """
        user_id = context.user_id
        model_key = kwargs.get("model_key")
        enable_thinking = kwargs.get("enable_thinking")

        # 获取当前配置
        current_config = user_config_manager.get_config(user_id)

        # 确定新配置值
        new_model_key = model_key if model_key is not None else current_config.model_key
        new_enable_thinking = (
            enable_thinking
            if enable_thinking is not None
            else current_config.enable_thinking
        )

        # 更新配置
        success = user_config_manager.update_config(
            user_id, new_model_key, new_enable_thinking
        )

        if success:
            logger.info(
                f"用户配置更新成功，user_id: {user_id}, model_key: {new_model_key}, enable_thinking: {new_enable_thinking}"
            )
            return f"配置更新成功！当前模型：{new_model_key}，深度思考：{'开启' if new_enable_thinking else '关闭'}"
        else:
            logger.error(f"用户配置更新失败，user_id: {user_id}")
            return "配置更新失败，请稍后重试"
