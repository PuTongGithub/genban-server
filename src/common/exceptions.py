"""自定义异常类"""


class EnvConfigNotFoundException(Exception):
    """环境配置未找到异常"""

    def __init__(self, key: str):
        super().__init__(f"env config:{key} not found")


class UserIdNotFoundException(Exception):
    """用户ID未找到异常"""

    def __init__(self, user_id: str):
        super().__init__(f"userId:{user_id} not found")


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


class ToolNotExistException(Exception):
    """工具不存在异常"""

    def __init__(self, tool_name: str):
        super().__init__(f"tool:{tool_name} not found")


class ModelNotFoundException(Exception):
    """模型未找到异常"""

    def __init__(self, model_name: str):
        super().__init__(f"model:{model_name} not found")
