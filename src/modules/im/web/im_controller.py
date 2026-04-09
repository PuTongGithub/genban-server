"""IM 模块路由"""

from fastapi import APIRouter, Depends

from src.common.logger import get_logger
from src.gateway.im.manager.credential_manager import credential_manager
from src.gateway.im.manager.im_manager import IMManager
from src.modules.im.web.entities import (
    ChannelTypeInfo,
    CredentialCreateRequest,
    CredentialCreateResponse,
    CredentialDeleteRequest,
    CredentialInfo,
    CredentialListResponse,
    CredentialToggleRequest,
    CredentialToggleResponse,
    CredentialUpdateRequest,
    CredentialUpdateResponse,
)
from src.user.auth import get_current_user_id

logger = get_logger(__name__)
router = APIRouter(prefix="/api/im", tags=["im"])


@router.get("/channels/list")
async def list_channels() -> list[ChannelTypeInfo]:
    """获取支持的渠道类型列表"""
    try:
        channel_types = IMManager.get_instance().list_channel_types()
        result = []
        for channel_class in channel_types:
            result.append(
                ChannelTypeInfo(
                    type=channel_class.channel_type,
                    name=channel_class.channel_name,
                    description=channel_class.channel_description,
                    credential_schema=[
                        {
                            "field_name": s.field_name,
                            "field_type": s.field_type,
                            "description": s.description,
                            "required": s.required,
                            "default_value": s.default_value,
                        }
                        for s in channel_class().credential_schema
                    ],
                )
            )
        return result
    except Exception:
        logger.exception("获取渠道类型列表失败")
        return []


@router.get("/credentials/list")
async def list_credentials(
    user_id: str = Depends(get_current_user_id),
) -> CredentialListResponse:
    """获取用户的凭证配置列表"""
    try:
        credentials = credential_manager.get_credentials(user_id)
        credential_infos = [
            CredentialInfo(
                id=c.id,
                channel_type=c.channel_type,
                enabled=c.enabled,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in credentials
        ]
        return CredentialListResponse(credentials=credential_infos)
    except Exception as e:
        logger.exception(f"获取凭证列表失败，user_id: {user_id}")
        return CredentialListResponse(credentials=[], error=str(e))


@router.post("/credentials/create")
async def create_credential(
    request: CredentialCreateRequest,
    user_id: str = Depends(get_current_user_id),
) -> CredentialCreateResponse:
    """创建凭证配置"""
    try:
        credential = credential_manager.create_credential(
            user_id=user_id,
            channel_type=request.channel_type,
            credential_data=request.credential_data,
        )
        if credential:
            return CredentialCreateResponse(success=True, credential_id=credential.id)
        else:
            return CredentialCreateResponse(error="创建凭证失败")
    except Exception as e:
        logger.exception(f"创建凭证失败，user_id: {user_id}, channel_type: {request.channel_type}")
        return CredentialCreateResponse(error=str(e))


@router.post("/credentials/update")
async def update_credential(
    request: CredentialUpdateRequest,
    user_id: str = Depends(get_current_user_id),
) -> CredentialUpdateResponse:
    """更新凭证配置"""
    try:
        success = credential_manager.update_credential(
            credential_id=request.credential_id,
            user_id=user_id,
            credential_data=request.credential_data,
            enabled=request.enabled,
        )
        if success:
            return CredentialUpdateResponse(success=True)
        else:
            return CredentialUpdateResponse(error="更新凭证失败")
    except Exception as e:
        logger.exception(
            f"更新凭证失败，user_id: {user_id}, credential_id: {request.credential_id}"
        )
        return CredentialUpdateResponse(error=str(e))


@router.post("/credentials/delete")
async def delete_credential(
    request: CredentialDeleteRequest,
    user_id: str = Depends(get_current_user_id),
) -> CredentialUpdateResponse:
    """删除凭证配置"""
    try:
        success = credential_manager.delete_credential(request.credential_id, user_id)
        if success:
            return CredentialUpdateResponse(success=True)
        else:
            return CredentialUpdateResponse(error="删除凭证失败")
    except Exception as e:
        logger.exception(
            f"删除凭证失败，user_id: {user_id}, credential_id: {request.credential_id}"
        )
        return CredentialUpdateResponse(error=str(e))


@router.post("/credentials/toggle")
async def toggle_credential(
    request: CredentialToggleRequest,
    user_id: str = Depends(get_current_user_id),
) -> CredentialToggleResponse:
    """启用/禁用凭证"""
    try:
        success = credential_manager.update_credential(
            credential_id=request.credential_id,
            user_id=user_id,
            enabled=request.enabled,
        )
        if success:
            return CredentialToggleResponse(success=True)
        else:
            return CredentialToggleResponse(error="操作失败")
    except Exception as e:
        logger.exception(
            f"切换凭证状态失败，user_id: {user_id}, credential_id: {request.credential_id}"
        )
        return CredentialToggleResponse(error=str(e))
