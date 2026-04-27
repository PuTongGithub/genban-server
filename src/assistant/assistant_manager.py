"""AgentManager - 管理所有用户的 Agent 实例"""

import threading
from typing import Callable

from src.agent.entities import Chat, MessagePipeContent
from src.assistant.assistant import Assistant
from src.common.logger import get_logger

logger = get_logger(__name__)


class AssistantManager:
    """管理所有用户的 Assistant 实例"""

    def __init__(self) -> None:
        self._assistants: dict[str, Assistant] = {}
        self._lock = threading.Lock()

    def _get_assistant(
        self,
        user_id: str,
    ) -> Assistant:
        """获取用户专属的 Assistant 实例"""
        if user_id not in self._assistants:
            with self._lock:
                if user_id not in self._assistants:
                    self._assistants[user_id] = Assistant(user_id=user_id)
        return self._assistants[user_id]

    def submit_chat(self, user_id: str, chats: list[Chat]) -> None:
        """将消息发送给用户 Assistant"""
        self._get_assistant(user_id).send_chat(chats)

    def stop_generation(self, user_id: str) -> None:
        """停止用户的生成过程"""
        if user_id in self._assistants:
            self._assistants[user_id].stop_generation()
            logger.info(f"已发送停止生成指令，user_id: {user_id}")
        else:
            logger.warning(f"用户 {user_id} 没有活跃的 Assistant，无法停止生成")

    def register_listener(
        self,
        user_id: str,
        listener_name: str,
        listener: Callable[[MessagePipeContent], None],
    ) -> None:
        """注册用户 Assistant 监听器"""
        self._get_assistant(user_id).register_listener(listener_name, listener)

    def unregister_listener(
        self,
        user_id: str,
        listener_name: str,
    ) -> None:
        """注销用户 Assistant 监听器"""
        self._get_assistant(user_id).unregister_listener(listener_name)


assistant_manager = AssistantManager()
