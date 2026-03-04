"""自定义异常类"""


class UserNotFoundException(Exception):
    """用户未找到异常"""

    def __init__(self, user_id: str):
        super().__init__(f"user:{user_id} not found")


class UnauthorizedException(Exception):
    """未授权异常"""

    def __init__(self):
        super().__init__("unauthorized")


class InvalidPasswordException(Exception):
    """密码无效异常"""

    def __init__(self):
        super().__init__("invalid password")


class WeakPasswordException(Exception):
    """密码强度不足异常"""

    def __init__(self, message: str = "password is too weak"):
        super().__init__(message)
