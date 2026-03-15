"""UserAgentWorker - 单个用户的 AgentWorker，复用 Agent 实例"""

from src.agent.agent import Agent
from src.agent.chat_factory import chat_factory
from src.agent.entities import Chat
from src.modules.memory.conversation_manager import conversation_manager
from src.modules.user_message.stream_manager import stream_manager
from src.modules.file_system.file_system_module import FileSystemModule
from src.modules.shell.shell_module import ShellModule
from src.modules.user_message.user_message_module import UserMessageModule
from src.modules.system_remainder.system_remainder_module import SystemRemainderModule
from src.modules.settings.settings_module import SettingsModule
from src.modules.skills.skills_module import SkillsModule
from src.modules.web.web_module import WebModule
from src.modules.memory.memory_module import MemoryModule
from src.modules.schedule.schedule_module import ScheduleModule
from src.common.logger import get_logger

logger = get_logger(__name__)


class UserAgentWorker:
    """单个用户的 AgentWorker - 复用 Agent 实例"""

    def __init__(self, user_id: str):
        """初始化用户专属的 AgentWorker"""
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

        self._agent = Agent(
            user_id=user_id,
            modules=modules,
        )

    async def process_chat(self, chat: Chat) -> None:
        """处理单个 Chat"""
        try:
            # 使用复用的 Agent 执行调用
            new_chats = self._agent.run(chat=chat)

            # 将新增的 Chat 添加到历史
            conversation_manager.add_chats(self.user_id, new_chats)

        except Exception as e:
            logger.exception(f"处理用户消息失败，user_id: {self.user_id}")

            # 创建错误 Chat
            error_chat = chat_factory.create_error_chat(
                content=f"处理消息时出错: {str(e)}"
            )
            conversation_manager.add_chat(self.user_id, error_chat)

            # 推送错误消息到 SSE
            stream_manager.push_chat(self.user_id, error_chat)
