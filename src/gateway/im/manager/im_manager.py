"""IM 管理器 - 管理 IM 渠道的注册、启动、消息路由和生命周期"""

import threading
from typing import Type

from src.agent.entities import Chat, ChatType
from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger
from src.gateway.im.manager.base_channel import BaseIMChannel
from src.gateway.im.manager.credential_manager import credential_manager
from src.gateway.im.manager.entities import ChannelNotFoundError, IMCredentialConfig, IMMessage

logger = get_logger(__name__)


class IMManager:
    """IM 管理器，负责渠道注册、实例管理、消息路由和生命周期管理"""

    im_manager = None

    @classmethod
    def get_instance(cls) -> "IMManager":
        """获取 IMManager 实例"""
        if cls.im_manager is None:
            cls.im_manager = IMManager()
            try:
                from src.gateway.im.qq.qq_channel import QQChannel

                cls.im_manager._register_channel(QQChannel())

                cls.im_manager._start_all_channels()
            except ImportError:
                logger.debug("QQ 渠道未实现，跳过注册")
            except Exception:
                logger.exception("注册 QQ 渠道失败")
        return cls.im_manager

    def __init__(self) -> None:
        self._channels: dict[str, BaseIMChannel] = {}
        self._lock = threading.Lock()
        self._executor = AsyncExecutor(name="IMManager", on_stop=self._stop_all_channels)
        credential_manager.register_update_callback(self._update_credential)

    def _register_channel(self, channel: BaseIMChannel) -> None:
        """注册渠道类型"""
        self._channels[channel.channel_type] = channel

    def _get_channel(self, channel_type: str) -> BaseIMChannel | None:
        """获取渠道实例，不存在则抛出异常。"""
        if channel_type in self._channels:
            return self._channels[channel_type]
        raise ChannelNotFoundError(channel_type)

    def _start_all_channels(self) -> None:
        """启动所有渠道"""
        credentials = credential_manager.list_enabled_credentials()
        for channel in self._channels.values():
            channel.start(credentials)
            channel.set_message_handler(self._on_im_message_received)
        logger.info("所有渠道启动完成")

    def _stop_all_channels(self) -> None:
        """停止所有渠道"""
        cs = list(self._channels.values())
        for channel in cs:
            try:
                channel.stop()
                self._channels.pop(channel.channel_type)
            except Exception:
                logger.exception(f"停止渠道失败: channel_type={channel.channel_type}")
        logger.info("所有渠道已停止")

    def _update_credential(
        self, im_credential: IMCredentialConfig, is_deleted: bool = False
    ) -> None:
        """更新或删除凭证配置"""
        channel = self._get_channel(im_credential.channel_type)
        channel.update_credential(im_credential.user_id, im_credential, is_deleted)
        action = "已删除" if is_deleted else "已更新"
        logger.info(
            f"凭证{action}: user_id={im_credential.user_id}, channel_type={im_credential.channel_type}"
        )

    def _on_im_message_received(self, message: IMMessage) -> None:
        """处理 IM 消息，转换为 Chat 并提交给 Assistant"""
        from src.agent.chat_factory import chat_factory
        from src.assistant.assistant_manager import assistant_manager

        try:
            chat = chat_factory.create_user_chat(
                message.user_id, message.content, message.channel_type
            )
            assistant_manager.submit_chat(message.user_id, [chat])
        except Exception:
            logger.exception(f"处理 IM 消息失败: user_id={message.user_id}")

    def _on_assistant_message(self, user_id: str, chats: list[Chat]) -> None:
        """处理 Assistant 消息，分发给 IM 渠道"""
        user_chat_channel_type = None
        user_content = None
        assistant_contents = []
        for chat in chats:
            if chat.type == ChatType.USER.type:
                user_chat_channel_type = chat.extra.channel_type
                user_content = (
                    f"[用户消息|来自{chat.extra.channel_type}]\n"
                    + chat.get_cleaned_message_content_text()
                )
            elif chat.type == ChatType.ASSISTANT.type:
                text = chat.message.get_text_content().lstrip()
                if text.startswith("[no_reply]") or not text:
                    continue
                if chat.message.reasoning_content:
                    assistant_contents.append(f"思考过程：\n{chat.message.reasoning_content}")
                assistant_contents.append(text)

        channels = list(self._channels.values())
        for channel in channels:
            try:
                if user_content is not None and channel.channel_type != user_chat_channel_type:
                    messages = [user_content] + assistant_contents
                else:
                    messages = assistant_contents
                self._executor.submit(channel.send_messages(user_id, messages))
            except Exception:
                logger.exception(
                    f"分发消息失败: user_id={user_id}, channel_type={channel.channel_type}"
                )

    def list_channel_types(self) -> list[Type[BaseIMChannel]]:
        """列出所有支持的渠道类型"""
        return list(channel.__class__ for channel in self._channels.values())
