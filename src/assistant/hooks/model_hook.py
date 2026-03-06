"""ModelHook 实现 - 设置默认模型"""

from src.agent.hooks.base_hook import ModelHook
from src.agent.entities import AgentContext
from src.config.config import app_config


class DefaultModelHook(ModelHook):
    """设置默认模型的钩子"""

    def execute(self, data: str | None, context: AgentContext) -> str | None:
        """返回默认模型 key

        Args:
            data: 默认模型 key，可能为 None
            context: Agent 执行上下文

        Returns:
            最终使用的模型 key
        """
        # 返回配置的默认模型
        return app_config.get_default_model()
