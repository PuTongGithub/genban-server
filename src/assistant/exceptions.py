class AssistantNotFoundException(Exception):
    """用户没有 Assistant 实例异常"""

    def __init__(self, message: str):
        super().__init__(message)
