"""IM 凭证更新工具"""

import json
from typing import Any

from src.agent.entities import AgentContext
from src.agent.tools.base_tool import BaseTool
from src.agent.tools.entities import ToolParameter
from src.common.logger import get_logger
from src.gateway.im.manager.credential_manager import credential_manager

logger = get_logger(__name__)


class IMUpdateTool(BaseTool):
    """IM 配置更新工具"""

    name = "im_credential_update"
    description = "更新IM渠道凭证配置，参数不传则保持不变"
    parameters = [
        ToolParameter(
            name="credential_id",
            type="integer",
            description="配置ID",
            required=True,
        ),
        ToolParameter(
            name="credential_data",
            type="object",
            description='新的凭证数据，如{"app_id":"xxx"}',
            required=False,
        ),
        ToolParameter(
            name="enabled",
            type="boolean",
            description="是否启用该渠道",
            required=False,
        ),
    ]

    def execute(self, context: AgentContext, **kwargs: Any) -> str:
        """执行更新凭证操作

        Args:
            context: Agent 执行上下文
            credential_id: 凭证ID
            credential_data: 新的凭证数据
            enabled: 是否启用

        Returns:
            更新结果JSON字符串
        """
        user_id = context.user_id
        credential_id = kwargs.get("credential_id")
        credential_data = kwargs.get("credential_data")
        enabled = kwargs.get("enabled")

        if not credential_id:
            return json.dumps({"error": "credential_id为必填参数"}, ensure_ascii=False)

        try:
            success = credential_manager.update_credential(
                credential_id=credential_id,
                user_id=user_id,
                credential_data=credential_data,
                enabled=enabled,
            )
            if success:
                return json.dumps({"success": True, "message": "凭证更新成功"}, ensure_ascii=False)
            else:
                return json.dumps({"success": False, "error": "凭证更新失败"}, ensure_ascii=False)
        except Exception as e:
            logger.exception(f"更新IM凭证失败，user_id: {user_id}, credential_id: {credential_id}")
            return json.dumps({"error": f"更新失败: {str(e)}"}, ensure_ascii=False)
