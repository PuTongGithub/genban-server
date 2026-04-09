"""IM 凭证创建工具"""

import json
from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.gateway.im.manager.credential_manager import credential_manager

logger = get_logger(__name__)


class IMCreateTool(BaseTool):
    """IM 凭证创建工具"""

    name = "im_credential_create"
    description = """新建一个IM渠道配置，创建后渠道默认启用。各渠道所需凭证：
- qq：app_id（机器人 AppID）， app_secret（机器人 AppSecret）"""
    parameters = [
        ToolParameter(
            name="channel_type",
            type="string",
            description="渠道类型，如 qq",
            required=True,
        ),
        ToolParameter(
            name="credential_data",
            type="object",
            description='凭证数据，如{"app_id":"xxx","app_secret":"xxx"}',
            required=True,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行创建凭证操作

        Args:
            context: Agent 执行上下文
            channel_type: 渠道类型
            credential_data: 凭证数据

        Returns:
            创建结果JSON字符串
        """
        user_id = context.user_id
        channel_type = kwargs.get("channel_type")
        credential_data = kwargs.get("credential_data")

        if not channel_type or not credential_data:
            return json.dumps(
                {"error": "channel_type和credential_data为必填参数"}, ensure_ascii=False
            )

        try:
            credential = credential_manager.create_credential(
                user_id=user_id,
                channel_type=channel_type,
                credential_data=credential_data,
            )
            if credential:
                return json.dumps(
                    {"success": True, "credential_id": credential.id, "message": "凭证创建成功"},
                    ensure_ascii=False,
                )
            else:
                return json.dumps({"success": False, "error": "凭证创建失败"}, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"创建IM凭证失败，user_id: {user_id}, channel_type: {channel_type}")
            return json.dumps({"error": f"创建失败: {str(e)}"}, ensure_ascii=False)
