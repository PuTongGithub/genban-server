"""QQ 渠道实体定义"""


class QQMessageSendError(Exception):
    """QQ 消息发送错误异常"""

    def __init__(self, message: str):
        super().__init__(message)
