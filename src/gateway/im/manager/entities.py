"""IM 渠道实体定义"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class IMMessage(BaseModel):
    """IM 消息实体"""

    user_id: str
    channel_type: str
    content: str
    file_paths: list[str] = []
    raw_data: dict[str, Any] = {}


class IMCredentialConfig(BaseModel):
    """IM 渠道凭证配置"""

    id: int
    user_id: str
    channel_type: str
    credential_data: str
    identity_data: str | None = None
    enabled: bool = True
    created_at: int = 0
    updated_at: int = 0


class DuplicateEnabledCredentialError(Exception):
    """同一用户、同一渠道类型已存在启用凭证异常"""

    def __init__(self, user_id: str, channel_type: str) -> None:
        self.user_id = user_id
        self.channel_type = channel_type
        super().__init__(f"用户 {user_id} 的 {channel_type} 渠道已存在启用凭证，请先禁用后再操作")


class ChannelSchemaFieldType(StrEnum):
    """渠道凭证字段类型"""

    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"


class ChannelSchema(BaseModel):
    """渠道凭证配置结构"""

    field_name: str
    field_type: ChannelSchemaFieldType = ChannelSchemaFieldType.STRING
    description: str = ""
    required: bool = True
    default_value: str | None = None


class ChannelNotFoundError(Exception):
    """渠道未找到异常"""

    def __init__(self, channel_type: str) -> None:
        super().__init__(f"渠道未找到: {channel_type}")
