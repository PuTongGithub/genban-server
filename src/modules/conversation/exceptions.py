class ContextCompressionError(Exception):
    """上下文压缩错误异常"""

    def __init__(self, message: str):
        super().__init__(message)
