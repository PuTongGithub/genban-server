"""用户模块路由"""

import traceback
from fastapi import APIRouter
from src.user.entity import LoginRequest, LoginResponse
from src.user.user_manager import user_manager


router = APIRouter(prefix="/user", tags=["user"])


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
