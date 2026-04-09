"""IM 凭证查询工具"""

import json

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.common.logger import get_logger
from src.gateway.im.manager.credential_manager import credential_manager

logger = get_logger(__name__)


class IMListTool(BaseTool):
    """IM 配置查询工具"""

    name = "im_list"
    description = "查询用户已配置的IM渠道配置列表"
    parameters = []

    def execute(self, context: AgentContext, **kwargs) -> str:
        """执行查询操作

        Args:
            context: Agent 执行上下文

        Returns:
            查询结果JSON字符串
        """
        user_id = context.user_id

        try:
            credentials = credential_manager.get_credentials(user_id)
            result = [
                {"id": c.id, "channel_type": c.channel_type, "enabled": c.enabled}
                for c in credentials
            ]
            return json.dumps({"success": True, "credentials": result}, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"IM配置查询失败，user_id: {user_id}")
            return json.dumps({"error": f"查询失败: {str(e)}"}, ensure_ascii=False)
