"""UserAgentWorker - 单个用户的 AgentWorker，复用 Agent 实例"""

import traceback
from src.agent.agent import Agent
from src.agent.chat_factory import chat_factory
from src.agent.entities import Chat
from src.assistant.conversation_manager import conversation_manager
from src.assistant.hooks.model_hook import DefaultModelHook
from src.assistant.hooks.prompt_hook import PromptSetupHook
from src.assistant.hooks.chats_hook import HistoryChatsHook
from src.assistant.hooks.stream_hook import StreamNewChatHook
from src.assistant.web.stream_manager import stream_manager
from src.modules.file_system.tools.read_file_tool import ReadFileTool
from src.modules.file_system.tools.write_file_tool import WriteFileTool
from src.modules.file_system.tools.edit_file_tool import EditFileTool
from src.modules.shell.shell_tool import ShellTool
from src.modules.skills.skill_tool import SkillTool


class UserAgentWorker:
    """单个用户的 AgentWorker - 复用 Agent 实例"""

    def __init__(self, user_id: str):
        """初始化用户专属的 AgentWorker"""
        self.user_id = user_id
        # 复用同一个 Agent 实例
        self._agent = Agent(
            user_id=user_id,
            hooks=[
                DefaultModelHook(),
                PromptSetupHook(),
                HistoryChatsHook(),
                StreamNewChatHook(),
            ],
            tools=[
                ReadFileTool(),
                WriteFileTool(),
                EditFileTool(),
                ShellTool(),
                SkillTool(),
            ],
        )

    async def process_chat(self, chat: Chat) -> None:
        """处理单个 Chat"""
        try:
            # 使用复用的 Agent 执行调用
            new_chats = self._agent.run(chat=chat)

            # 将新增的 Chat 添加到历史
            conversation_manager.add_chats(self.user_id, new_chats)

        except Exception as e:
            traceback.print_exc()

            # 创建错误 Chat
            error_chat = chat_factory.create_error_chat(
                content=f"处理消息时出错: {str(e)}"
            )
            conversation_manager.add_chat(self.user_id, error_chat)

            # 推送错误消息到 SSE
            stream_manager.push_chat(self.user_id, error_chat)
