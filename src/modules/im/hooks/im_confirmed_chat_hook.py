"""IM 确认对话钩子 - 将 Assistant 消息分发给 IM 渠道"""

from src.agent.entities import AgentContext, Chat
from src.agent.hooks.base_hook import ConfirmedChatHook
from src.common.logger import get_logger
from src.gateway.im.manager.im_manager import IMManager

logger = get_logger(__name__)


class IMConfirmedChatHook(ConfirmedChatHook):
    """处理已确认的 Assistant 对话，将消息分发给 IM 渠道"""

    order = 50  # 执行顺序，数值越小越先执行

    def execute(self, data: list[Chat] | None, context: AgentContext) -> list[Chat] | None:
        """执行钩子逻辑，将 Assistant 消息分发给 IM 渠道

        Args:
            data: 已确认的新增对话列表
            context: Agent 执行上下文

        Returns:
            处理后的对话列表（原样返回）
        """
        if not data:
            return data

        try:
            IMManager.get_instance()._on_assistant_message(context.user_id, data)
        except Exception:
            logger.exception(f"分发消息到 IM 渠道失败: user_id={context.user_id}")

        return data
