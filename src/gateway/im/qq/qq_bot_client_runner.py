"""QQ 机器人客户端运行器

使用 ThreadExecutor 在线程中运行 QQBotClient，支持 C2C 单聊消息处理
"""

import asyncio
from typing import Callable

from botpy.message import C2CMessage

from src.common.async_executor import AsyncExecutor
from src.common.logger import get_logger
from src.gateway.im.qq.qq_bot_client import QQBotClient

logger = get_logger(__name__)


class QQBotClientRunner:
    """QQ 机器人客户端运行器"""

    def __init__(
        self,
        user_id: str,
        credential_id: int,
        app_id: str,
        app_secret: str,
        identity: dict,
        message_handler: Callable[[str, C2CMessage], None],
        identity_update_handler: Callable[[str, int, dict], None],
    ) -> None:
        """初始化 QQ 机器人客户端运行器

        Args:
            user_id: 用户 ID，格式为 "guild_id:channel_id"
            credential_id: 凭证 ID
            app_id: QQ 机器人应用 ID
            app_secret: QQ 机器人应用密钥
            identity: 身份信息字典
            message_handler: 消息处理回调函数
            identity_update_handler: 身份信息更新回调函数
        """
        self._user_id = user_id
        self._credential_id = credential_id
        self._app_id = app_id
        self._app_secret = app_secret
        self._message_handler = message_handler
        self._identity_update_handler = identity_update_handler
        self._identity = identity
        self._client: QQBotClient | None = None
        self._executor: AsyncExecutor = AsyncExecutor(
            name=f"QQBotRunner-{self._user_id}",
            on_stop=self._on_stop,
        )

    async def _run_client(self) -> None:
        """在线程中运行 QQ 机器人客户端"""
        try:
            self._client = QQBotClient(
                message_handler=self._on_message_handler,
                identity_update_handler=self._on_identity_update_handler,
                identity=self._identity,
            )
            async with self._client:
                # 使用 create_task 让 start 在后台运行，这样可以通过取消任务来停止
                task = asyncio.create_task(
                    self._client.start(appid=self._app_id, secret=self._app_secret)
                )
                # 等待任务完成或被取消
                try:
                    await task
                except asyncio.CancelledError:
                    raise
        except asyncio.CancelledError:
            # 正常取消，不需要记录异常
            pass
        except Exception as e:
            logger.exception(f"QQ 机器人客户端运行异常: {e}")

    def _on_message_handler(self, message: C2CMessage) -> None:
        """处理 QQ 消息"""
        self._message_handler(self._user_id, message)

    def _on_identity_update_handler(self, identity: dict) -> None:
        """处理 QQ 身份信息更新"""
        self._identity_update_handler(self._user_id, self._credential_id, identity)

    def start(self) -> None:
        """启动 QQ 机器人客户端"""
        self._executor.submit(self._run_client())

    def stop(self, timeout: float | None = None) -> None:
        """停止 QQ 机器人客户端

        Args:
            timeout: 等待线程停止的超时时间（秒）
        """
        self._executor.stop(timeout=timeout)
        logger.info(f"QQ 机器人客户端已停止: user_id={self._user_id}")

    def _on_stop(self) -> None:
        """停止时的回调函数"""
        if self._client and self._executor.is_running():
            try:
                # 关闭 botpy 客户端
                self._executor.submit(self._client.close())
            except Exception as e:
                logger.exception(f"关闭 QQ 机器人客户端时发生异常: {e}")

    def send_messages(self, contents: list[str]) -> None:
        """发送消息"""
        if self._client is not None and self._executor.is_running():
            self._executor.submit(self._client.send_messages(contents))
