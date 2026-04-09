"""IM 渠道抽象基类"""

from abc import ABC, abstractmethod
from typing import Callable, ClassVar

from src.gateway.im.manager.credential_manager import credential_manager
from src.gateway.im.manager.entities import ChannelSchema, IMCredentialConfig, IMMessage


class BaseIMChannel(ABC):
    """IM 渠道抽象基类"""

    channel_type: ClassVar[str] = ""
    channel_name: ClassVar[str] = ""
    channel_description: ClassVar[str] = ""
    credential_schema: ClassVar[list[ChannelSchema]] = []

    def __init__(self) -> None:
        self._message_received_handler: Callable[[IMMessage], None] | None = None

    def set_message_handler(self, handler: Callable[[IMMessage], None]) -> None:
        """设置消息接收回调函数"""
        self._message_received_handler = handler

    def _on_message_received(self, message: IMMessage) -> None:
        """消息接收回调，子类调用此方法将消息传递给管理器"""
        if self._message_received_handler:
            self._message_received_handler(message)

    def _handle_identity_update(self, user_id: str, credential_id: int, identity: dict) -> None:
        """处理身份信息更新

        Args:
            user_id: 用户 ID
            credential_id: 凭证 ID
            identity: 身份信息字典
        """
        credential_manager.update_identity_data(
            credential_id=credential_id, user_id=user_id, identity_data=identity
        )

    @abstractmethod
    def start(self, im_credentials: list[IMCredentialConfig]) -> None:
        """启动渠道连接"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """停止渠道连接"""
        pass

    @abstractmethod
    async def send_messages(self, user_id: str, contents: list[str]) -> None:
        """发送消息

        Args:
            user_id: 用户 ID
            contents: 消息内容列表
        """
        pass

    @abstractmethod
    def update_credential(
        self, user_id: str, im_credential: IMCredentialConfig | None, is_deleted: bool = False
    ) -> None:
        """更新或删除凭证配置

        Args:
            user_id: 用户 ID
            im_credential: 凭证配置，删除时为 None
            is_deleted: 是否为删除操作
        """
        pass
