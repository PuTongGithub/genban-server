"""自定义异常类"""

from fastapi import HTTPException
from fastapi import status


class UserNotFoundException(Exception):
    """用户未找到异常"""

    def __init__(self, user_id: str):
        super().__init__(f"user:{user_id} not found")


class InvalidPasswordException(Exception):
    """密码无效异常"""

    def __init__(self):
        super().__init__("invalid password")


class WeakPasswordException(Exception):
    """密码强度不足异常"""

    def __init__(self, message: str = "password is too weak"):
        super().__init__(message)


class UserNotAllowedException(Exception):
    """用户不在白名单异常"""

    def __init__(self, user_id: str):
        super().__init__(f"user:{user_id} not in allowed list")


class InvalidUsernameException(Exception):
    """用户名格式不合法异常"""

    def __init__(self, message: str = "username is invalid"):
        super().__init__(message)


class UnauthorizedException(HTTPException):
    """未授权异常 - FastAPI HTTPException 版本"""

    def __init__(self, detail: str = "未授权，请重新登录"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
