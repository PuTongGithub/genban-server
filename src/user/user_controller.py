"""用户模块路由"""

from fastapi import APIRouter

from src.common.logger import get_logger
from src.config.config import file_config
from src.user.entity import LoginRequest, LoginResponse, PublicKeyResponse
from src.user.user_manager import user_manager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/login")
async def login(request: LoginRequest) -> LoginResponse:
    # 用户登录/自动注册接口，password字段为RSA加密后的密文
    # 若用户不存在则自动注册，存在则验证登录
    try:
        user_token = user_manager.login_or_register(request.user_id, request.password)
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
