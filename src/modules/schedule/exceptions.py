"""日程模块异常类"""


class InvalidCronExpressionException(Exception):
    """无效的 cron 表达式异常"""

    def __init__(self, message: str = "cron表达式格式错误"):
        super().__init__(message)
