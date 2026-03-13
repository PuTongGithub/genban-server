"""ModelHook 实现 - 设置默认模型"""

from src.agent.hooks.base_hook import ModelHook
from src.agent.entities import AgentContext, ModelConfig
from src.user.user_config_manager import user_config_manager


class DefaultModelHook(ModelHook):
    """设置默认模型的钩子"""

    def execute(
        self, data: ModelConfig | None, context: AgentContext
    ) -> ModelConfig | None:
        """返回最终模型配置

        Args:
            data: 模型配置对象，可能为 None
            context: Agent 执行上下文

        Returns:
            最终使用的模型配置对象
        """
        return user_config_manager.get_config(context.user_id)
