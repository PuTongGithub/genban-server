"""Assistant 模块自定义异常"""

from fastapi import HTTPException
from fastapi import status


class UnauthorizedException(HTTPException):
    """未授权异常 - FastAPI HTTPException 版本"""

    def __init__(self, detail: str = "未授权，请重新登录"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class MessageQueueError(Exception):
    """消息队列异常"""

    def __init__(self, message: str = "消息队列异常"):
        super().__init__(message)
