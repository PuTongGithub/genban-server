from typing import Callable
from src.agent.agent import Agent
from src.agent.entities import Chat, chatTypeMap
from src.modules.file_system.file_system_module import FileSystemModule
from src.modules.shell.shell_module import ShellModule
from src.modules.user_message.user_message_module import UserMessageModule
from src.modules.system_remainder.system_remainder_module import SystemRemainderModule
from src.modules.settings.settings_module import SettingsModule
from src.modules.skills.skills_module import SkillsModule
from src.modules.web.web_module import WebModule
from src.modules.memory.memory_module import MemoryModule
from src.modules.schedule.schedule_module import ScheduleModule
from src.common.thread_executor import ThreadExecutor
from src.common.logger import get_logger
from src.common.utils import time_util
from src.config.config import app_config

logger = get_logger(__name__)


class Assistant:
    """助手类，用于管理用户与 Agent 的交互"""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id

        # 创建模块实例
        modules = [
            UserMessageModule(),
            SystemRemainderModule(),
            FileSystemModule(),
            ShellModule(user_id),
            SettingsModule(),
            SkillsModule(),
            WebModule(),
            MemoryModule(),
            ScheduleModule(),
        ]

        self.agent = Agent(user_id=user_id, modules=modules)
        self.listeners: dict[str, Callable[[Chat], None]] = {}
        self._executor = ThreadExecutor(
            name=f"Assistant-{self.user_id}",
            target=self._distribute_chat,
        )
        self._last_active_time = time_util.get_timestamp()
        self._executor.start()

    def send_chat(self, chat: Chat) -> None:
        """发送消息给 Agent"""
        self._last_active_time = time_util.get_timestamp()
        if not self._executor.is_running():
            self._executor.start()
        self.agent.send_chat(chat)

    def register_listener(
        self, listener_name: str, listener: Callable[[Chat], None]
    ) -> None:
        """注册消息监听器"""
        self._last_active_time = time_util.get_timestamp()
        if not self._executor.is_running():
            self._executor.start()
        self.listeners[listener_name] = listener

    def unregister_listener(self, listener_name: str) -> None:
        """注销消息监听器"""
        self._last_active_time = time_util.get_timestamp()
        self.listeners.pop(listener_name, None)

    def _should_stop(self) -> bool:
        """检查是否需要停止 Assistant"""
        # 快速失败：有监听器时不停止
        if len(self.listeners) > 0:
            return False

        inactive_timeout = app_config.get("assistant")["inactive_timeout"]
        inactive_time = time_util.get_timestamp() - self._last_active_time
        return inactive_time > inactive_timeout

    def _distribute_chat(self):
        """分发消息给所有监听器"""
        while True:
            try:
                # 检查是否已停止
                if not self._executor.is_running():
                    break

                # 每轮检查是否需要停止
                if self._should_stop():
                    self._executor.stop()
                    break

                # 等待新消息
                chat = self.agent.recv_chat()
                if chat is None:
                    continue

                # 检查消息类型是否用户可见
                chatType = chatTypeMap[chat.type]
                if not chatType.userVisible:
                    continue

                for listener_name, listener in self.listeners.items():
                    try:
                        listener(chat)
                    except Exception as e:
                        logger.exception(
                            f"助手监听器 {listener_name} 分发消息时出错: {e}"
                        )
            except Exception as e:
                logger.exception(f"助手分发消息时出错: {e}")
