"""用户配置相关实体定义"""

from pydantic import BaseModel
from typing import Optional


class GetSettingsResponse(BaseModel):
    # 获取用户配置响应
    model_key: str = ""
    enable_thinking: bool = False
    error: str = ""


class UpdateSettingsRequest(BaseModel):
    # 更新用户配置请求
    model_key: Optional[str] = None
    enable_thinking: Optional[bool] = None


class UpdateSettingsResponse(BaseModel):
    # 更新用户配置响应
    success: bool = False
    error: str = ""


class GetModelsResponse(BaseModel):
    # 获取可用模型列表响应
    models: list[str] = []  # 模型 key 列表
    error: str = ""
