"""IM 管理器 - 管理 IM 渠道的注册、启动、消息路由和生命周期"""

import threading
from typing import Type

from src.agent.entities import Chat, ChatType
from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger
from src.common.utils.path_util import get_user_dir
from src.gateway.im.manager.base_channel import BaseIMChannel
from src.gateway.im.manager.credential_manager import credential_manager
from src.gateway.im.manager.entities import ChannelNotFoundError, IMCredentialConfig, IMMessage
from src.storage.file.file_storage import file_storage

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
            chats = []
            if message.file_paths:
                file_chat = chat_factory.create_file_upload_chat(message.file_paths)
                chats.append(file_chat)
            message_content = "(一条来自渠道的消息)" if not message.content else message.content
            chat = chat_factory.create_user_chat(
                message.user_id, message_content, message.channel_type
            )
            chats.append(chat)
            assistant_manager.submit_chat(message.user_id, chats)
        except Exception:
            logger.exception(f"处理 IM 消息失败: user_id={message.user_id}")

    def _on_assistant_message(self, user_id: str, chats: list[Chat]) -> None:
        """处理 Assistant 消息，分发给 IM 渠道"""
        user_chat_channel_type = None
        user_content = None
        assistant_contents = []
        file_paths: list[str] = []
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
            elif chat.type == ChatType.FILE.type:
                file_text = chat.message.get_text_content()
                file_path = self._resolve_file_path(user_id, file_text)
                if file_path:
                    file_paths.append(file_path)

        channels = list(self._channels.values())
        for channel in channels:
            try:
                if file_paths:
                    for file_path in file_paths:
                        channel.send_file(user_id, file_path)
                if user_content is not None and channel.channel_type != user_chat_channel_type:
                    messages = [user_content] + assistant_contents
                else:
                    messages = assistant_contents
                if messages:
                    self._executor.submit(channel.send_messages(user_id, messages))
            except Exception:
                logger.exception(
                    f"分发消息失败: user_id={user_id}, channel_type={channel.channel_type}"
                )

    def _resolve_file_path(self, user_id: str, file_text: str) -> str | None:
        """解析并校验文件路径

        Args:
            user_id: 用户 ID
            file_text: Chat 中的文件路径文本

        Returns:
            绝对路径，文件不存在或路径非法返回 None
        """
        try:
            user_dir = get_user_dir(user_id)
            file_path = user_dir / file_text
            file_path = file_path.resolve()
            if not file_storage.exists(file_path) or not file_storage.is_file(file_path):
                logger.warning(f"文件不存在或不是文件: {file_path}")
                return None
            return str(file_path)
        except Exception as e:
            logger.warning(f"解析文件路径失败: user_id={user_id}, path={file_text}, error={e}")
            return None

    def list_channel_types(self) -> list[Type[BaseIMChannel]]:
        """列出所有支持的渠道类型"""
        return list(channel.__class__ for channel in self._channels.values())
