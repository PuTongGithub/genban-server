"""QQ 机器人客户端封装"""

import logging
from typing import Callable

import botpy
from botpy.manage import C2CManageEvent
from botpy.message import C2CMessage
from botpy.types.message import MarkdownPayload

from src.common.logger import get_logger
from src.gateway.im.qq.entities import QQMessageSendError

logger = get_logger(__name__)
intents = botpy.Intents(public_messages=True)


class QQBotClient(botpy.Client):
    """QQ 机器人客户端，继承自 botpy.Client"""

    def __init__(
        self,
        message_handler: Callable[[C2CMessage], None],
        identity_update_handler: Callable[[dict], None],
        identity: dict,
    ) -> None:
        """初始化 QQ 机器人客户端"""
        super().__init__(intents=intents, is_sandbox=True, bot_log=None, log_level=logging.INFO)
        self._message_handler: Callable[[C2CMessage], None] = message_handler
        self._identity_update_handler: Callable[[dict], None] = identity_update_handler
        self._identity: dict = identity

    def _get_user_openid(self, user_openid: str | None = None) -> str:
        """获取用户 OpenID"""
        if user_openid is None:
            user_openid = self._identity.get("user_openid")
            if user_openid is None:
                raise QQMessageSendError("user_openid 未获取到")
            return user_openid
        else:
            if user_openid != self._identity.get("user_openid"):
                self._identity["user_openid"] = user_openid
                self._identity_update_handler(self._identity)
            return user_openid

    async def on_ready(self) -> None:
        """机器人就绪回调"""
        logger.info(f"机器人 「{self.robot.name}」 已就绪!")

    async def on_friend_add(self, event: C2CManageEvent) -> None:
        """处理好友添加事件

        Args:
            event: 好友添加事件对象
        """
        logger.info(f"用户添加机器人: {str(event)}")
        self._get_user_openid(event.openid)

    async def on_c2c_message_create(self, message: C2CMessage) -> None:
        """处理 C2C消息事件

        Args:
            message: QQ 消息对象
        """
        logger.info(
            f"收到 QQ 消息: openid={message.author.user_openid}, content={message.content}, attachments={str(message.attachments)}"
        )

        self._get_user_openid(message.author.user_openid)

        try:
            self._message_handler(message)
        except Exception as e:
            logger.exception(f"处理 QQ 消息时发生异常: {e}")

    async def send_messages(self, contents: list[str]) -> None:
        """发送消息到指定子频道

        Args:
            contents: 消息内容列表
        """
        try:
            user_openid = self._get_user_openid()
            for content in contents:
                markdown = MarkdownPayload(content=content)
                await self.api.post_c2c_message(user_openid, msg_type=2, markdown=markdown)
        except Exception as e:
            logger.exception(f"发送 QQ 消息失败: user_openid={user_openid}, error={e}")
            raise
