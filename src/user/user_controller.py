"""用户模块路由"""

import traceback
from fastapi import APIRouter
from src.user.entity import LoginRequest, LoginResponse, PublicKeyResponse
from src.user.user_manager import user_manager
from src.config.config import file_config


router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    # 用户登录/自动注册接口，password字段为RSA加密后的密文
    # 若用户不存在则自动注册，存在则验证登录
    try:
        state = user_manager.login_or_register(request.user_id, request.password)
        return LoginResponse(token=state.token, expires_at=state.token_expires_at)
    except Exception as e:
        traceback.print_exc()
        return LoginResponse(error=str(e))


@router.get("/key")
async def get_public_key() -> PublicKeyResponse:
    # 获取RSA公钥，用于前端加密密码
    try:
        public_key = file_config.get_public_key()
        return PublicKeyResponse(public_key=public_key)
    except Exception as e:
        traceback.print_exc()
        return PublicKeyResponse(error=str(e))
