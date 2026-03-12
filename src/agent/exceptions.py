"""Agent 模块异常定义"""


class ModelProviderNotFoundException(Exception):
    """模型提供者未找到异常"""

    def __init__(self, model_name: str):
        super().__init__(f"model provider:{model_name} not found")


class ToolNotExistException(Exception):
    """工具不存在异常"""

    def __init__(self, tool_name: str):
        super().__init__(f"tool:{tool_name} not found")


class ModelCallException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ModelCallLengthLimitedException(Exception):
    def __init__(self):
        super().__init__("model call length limited")


class ModelResponseException(Exception):
    """模型响应异常"""

    def __init__(self, message: str, response: object | None = None):
        super().__init__(message)
        self.response = response
