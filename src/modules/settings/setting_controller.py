"""用户配置模块路由"""

from fastapi import APIRouter, Depends
from src.modules.settings.entities import (
    GetSettingsResponse,
    UpdateSettingsRequest,
    UpdateSettingsResponse,
    GetModelsResponse,
)
from src.user.user_config_manager import user_config_manager
from src.user.auth import get_current_user_id
from src.common.logger import get_logger
from src.config.config import app_config

logger = get_logger(__name__)

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/get")
async def get_settings(
    user_id: str = Depends(get_current_user_id),
) -> GetSettingsResponse:
    # 获取用户配置接口
    try:
        config = user_config_manager.get_config(user_id)
        return GetSettingsResponse(
            model_key=config.model_key, enable_thinking=config.enable_thinking
        )
    except Exception as e:
        logger.exception(f"获取用户配置失败，user_id: {user_id}")
        return GetSettingsResponse(error=str(e))


@router.post("/update")
async def update_settings(
    request: UpdateSettingsRequest, user_id: str = Depends(get_current_user_id)
) -> UpdateSettingsResponse:
    # 更新用户配置接口
    try:
        # 获取当前配置
        current_config = user_config_manager.get_config(user_id)
        # 根据请求参数更新配置
        model_key = (
            request.model_key
            if request.model_key is not None
            else current_config.model_key
        )
        enable_thinking = (
            request.enable_thinking
            if request.enable_thinking is not None
            else current_config.enable_thinking
        )
        # 保存配置
        success = user_config_manager.update_config(user_id, model_key, enable_thinking)
        return UpdateSettingsResponse(success=success)
    except Exception as e:
        logger.exception(f"更新用户配置失败，user_id: {user_id}")
        return UpdateSettingsResponse(success=False, error=str(e))


@router.get("/models")
async def get_models(
    user_id: str = Depends(get_current_user_id),
) -> GetModelsResponse:
    # 获取可用模型列表接口
    try:
        models_config = app_config.get("models")
        models = list(models_config.keys())
        return GetModelsResponse(models=models)
    except Exception as e:
        logger.exception("获取可用模型列表失败")
        return GetModelsResponse(error=str(e))
