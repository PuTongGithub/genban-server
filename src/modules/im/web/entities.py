"""IM 模块 Web 层实体定义"""

from typing import Any

from pydantic import BaseModel


class ChannelTypeInfo(BaseModel):
    """渠道类型信息"""

    type: str
    name: str
    description: str
    credential_schema: list[dict[str, Any]]


class CredentialInfo(BaseModel):
    """凭证信息"""

    id: int
    channel_type: str
    enabled: bool
    created_at: int
    updated_at: int


class CredentialCreateRequest(BaseModel):
    """创建凭证请求"""

    channel_type: str
    credential_data: dict[str, Any]


class CredentialCreateResponse(BaseModel):
    """创建凭证响应"""

    success: bool = False
    credential_id: int = 0
    error: str = ""


class CredentialUpdateRequest(BaseModel):
    """更新凭证请求"""

    credential_id: int
    credential_data: dict[str, Any] | None = None
    enabled: bool | None = None


class CredentialDeleteRequest(BaseModel):
    """删除凭证请求"""

    credential_id: int


class CredentialUpdateResponse(BaseModel):
    """更新凭证响应"""

    success: bool = False
    error: str = ""


class CredentialListResponse(BaseModel):
    """凭证列表响应"""

    credentials: list[CredentialInfo]
    error: str = ""


class CredentialToggleRequest(BaseModel):
    """启用/禁用凭证请求"""

    credential_id: int
    enabled: bool


class CredentialToggleResponse(BaseModel):
    """启用/禁用凭证响应"""

    success: bool = False
    error: str = ""
