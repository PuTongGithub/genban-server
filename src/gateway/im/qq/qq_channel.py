"""QQ 渠道实现"""

from typing import ClassVar

from pt_botpy.message import C2CMessage

from src.common.logger import get_logger
from src.gateway.im.manager.base_channel import BaseIMChannel
from src.gateway.im.manager.credential_manager import credential_manager
from src.gateway.im.manager.entities import (
    ChannelSchema,
    ChannelSchemaFieldType,
    IMCredentialConfig,
    IMMessage,
    IMMessageType,
)
from src.gateway.im.qq.entities import QQMessageSendError
from src.gateway.im.qq.qq_bot_client_runner import QQBotClientRunner

logger = get_logger(__name__)


class QQChannel(BaseIMChannel):
    """QQ 渠道实现"""

    channel_type: ClassVar[str] = "qq"
    channel_name: ClassVar[str] = "QQ频道"
    channel_description: ClassVar[str] = "QQ频道机器人，支持接收和发送消息"
    credential_schema: ClassVar[list[ChannelSchema]] = [
        ChannelSchema(
            field_name="app_id",
            field_type=ChannelSchemaFieldType.STRING,
            description="机器人 AppID",
            required=True,
        ),
        ChannelSchema(
            field_name="app_secret",
            field_type=ChannelSchemaFieldType.STRING,
            description="机器人 AppSecret",
            required=True,
        ),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client_runners: dict[str, QQBotClientRunner] = {}

    def _start_client(self, im_credential: IMCredentialConfig) -> QQBotClientRunner:
        """启动 QQ 机器人客户端"""
        credential_data = credential_manager.decrypt_data(im_credential.credential_data)
        if im_credential.identity_data is not None:
            identity = credential_manager.decrypt_data(im_credential.identity_data)
        else:
            identity = {}
        client = QQBotClientRunner(
            user_id=im_credential.user_id,
            credential_id=im_credential.id,
            app_id=credential_data["app_id"],
            app_secret=credential_data["app_secret"],
            identity=identity,
            message_handler=self._handle_message,
            identity_update_handler=self._handle_identity_update,
        )
        client.start()
        return client

    def _stop_client(self, user_id: str) -> None:
        """停止 QQ 机器人客户端"""
        client = self._client_runners.get(user_id)
        if client:
            client.stop()
            self._client_runners.pop(user_id)

    def start(self, im_credentials: list[IMCredentialConfig]) -> None:
        """启动 QQ 机器人"""
        for im_credential in im_credentials:
            if not im_credential.enabled or im_credential.channel_type != self.channel_type:
                continue
            self._client_runners[im_credential.user_id] = self._start_client(im_credential)
        logger.info("QQ 渠道启动成功")

    def stop(self) -> None:
        """停止 QQ 机器人"""
        logger.info("正在停止 QQ 渠道")
        while len(self._client_runners) > 0:
            user_id = next(iter(self._client_runners.keys()))
            self._stop_client(user_id)
        logger.info("QQ 渠道已停止")

    async def send_messages(self, user_id: str, contents: list[str]) -> None:
        """发送消息到 QQ 频道

        Args:
            user_id: 用户 ID，格式为 "guild_id:channel_id"
            contents: 消息内容列表
        """
        if user_id in self._client_runners:
            self._client_runners[user_id].send_messages(contents)
            logger.info(f"发送 QQ 消息成功: user_id={user_id}")
        else:
            raise QQMessageSendError("用户未启用 QQ 渠道")

    def update_credential(
        self, user_id: str, im_credential: IMCredentialConfig | None, is_deleted: bool = False
    ) -> None:
        """更新或删除 QQ 凭证

        Args:
            user_id: 用户 ID
            im_credential: 凭证配置，删除时为 None
            is_deleted: 是否为删除操作
        """
        # 停止现有客户端
        if user_id in self._client_runners:
            self._stop_client(user_id)

        # 如果是删除操作或凭证为 None，直接返回
        if is_deleted or im_credential is None:
            logger.info(f"QQ 凭证已删除: user_id={user_id}")
            return

        # 如果凭证启用，启动新客户端
        if im_credential.enabled:
            self._client_runners[user_id] = self._start_client(im_credential)
            logger.info(f"QQ 凭证已更新: user_id={user_id}")

    def _handle_message(self, user_id: str, message: C2CMessage) -> None:
        """处理 QQ 消息

        Args:
            message: QQ 消息对象
        """
        try:
            content = message.content
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    if attachment.content_type == "voice":
                        content = "（语音消息转文字：" + attachment.asr_refer_text + "）"

            im_message = IMMessage(
                user_id=user_id,
                channel_type=self.channel_type,
                content=content,
                message_type=IMMessageType.TEXT,
            )

            self._on_message_received(im_message)

            logger.info(f"收到 QQ 消息: user_id={user_id}, content={message.content}")
        except Exception as e:
            logger.exception(f"处理 QQ 消息时发生异常: {e}")
