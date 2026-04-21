"""用户模块路由"""

from fastapi import APIRouter, Depends, Request, Response

from src.common.logger import get_logger
from src.config.config import file_config
from src.user.auth import SESSION_COOKIE_NAME, get_current_user_id
from src.user.entity import (
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    PublicKeyResponse,
    UserInfoResponse,
    WebLoginResponse,
)
from src.user.user_manager import user_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    # 用户登录/自动注册接口，password字段为RSA加密后的密文
    # 若用户不存在则自动注册，存在则验证登录
    try:
        user_token = user_manager.login_or_register(
            request.user_id, request.password, request.invite_code
        )
        logger.info(f"用户登录成功，user_id: {request.user_id}")
        return LoginResponse(token=user_token.token, expires_at=user_token.expires_at)
    except Exception as e:
        logger.exception(f"用户登录失败，user_id: {request.user_id}")
        return LoginResponse(error=str(e))


@router.get("/key")
async def get_public_key() -> PublicKeyResponse:
    # 获取RSA公钥，用于前端加密密码
    try:
        public_key = file_config.get_public_key()
        logger.info("获取公钥成功")
        return PublicKeyResponse(public_key=public_key)
    except Exception:
        logger.exception("获取公钥失败")
        return PublicKeyResponse(error="获取公钥失败")


@router.post("/login-web")
async def login_web(request: LoginRequest, response: Response) -> WebLoginResponse:
    # Web端登录接口，登录成功后设置HttpOnly Cookie
    try:
        user_token = user_manager.login_or_register(
            request.user_id, request.password, request.invite_code
        )
        # 设置HttpOnly Cookie，有效期48小时
        response.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=user_token.token,
            httponly=True,
            samesite="lax",
            max_age=172800,
        )
        logger.info(f"Web用户登录成功，user_id: {request.user_id}")
        return WebLoginResponse(
            user_id=request.user_id, expires_at=user_token.expires_at
        )
    except Exception as e:
        logger.exception(f"Web用户登录失败，user_id: {request.user_id}")
        return WebLoginResponse(error=str(e))


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user_id: str = Depends(get_current_user_id),
) -> LogoutResponse:
    # 用户登出接口，清除Cookie并使session失效
    try:
        # 从Cookie中获取session
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        if session_id:
            # 删除token记录
            user_manager.logout(session_id)
        # 清除Cookie
        response.set_cookie(
            key=SESSION_COOKIE_NAME, value="", httponly=True, samesite="lax", max_age=0
        )
        logger.info(f"用户登出成功，user_id: {user_id}")
        return LogoutResponse(success=True)
    except Exception as e:
        logger.exception(f"用户登出失败，user_id: {user_id}")
        return LogoutResponse(error=str(e))


@router.get("/me")
async def get_current_user_info(
    user_id: str = Depends(get_current_user_id),
) -> UserInfoResponse:
    # 获取当前登录用户信息，用于前端页面刷新后恢复登录状态
    try:
        # 获取用户token信息以获取过期时间
        # 由于get_current_user_id已经验证了token/session的有效性
        # 这里直接从user_token_db查询用户的token信息
        from src.user.db.user_token_db import user_token_db

        user_tokens = user_token_db.get_tokens_by_user_id(user_id)
        if user_tokens:
            # 获取最新的token（过期时间最晚的）
            latest_token = max(user_tokens, key=lambda t: t.expires_at)
            logger.info(f"获取用户信息成功，user_id: {user_id}")
            return UserInfoResponse(
                user_id=user_id, expires_at=latest_token.expires_at
            )
        logger.warning(f"用户token不存在，user_id: {user_id}")
        return UserInfoResponse(error="用户会话不存在")
    except Exception as e:
        logger.exception(f"获取用户信息失败，user_id: {user_id}")
        return UserInfoResponse(error=str(e))
